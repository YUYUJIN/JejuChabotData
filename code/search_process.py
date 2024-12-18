import os
import json
import numpy as np
import pandas as pd
from tqdm import tqdm

AREA_GROUP={
    '제주시':['일도일동', '일도이동', '이도일동', '이도이동', '삼도일동', '삼도이동', '용담일동', '용담이동', '건입동', '화북동', '삼양동', '봉개동', '아라동', '오라동', '연동', '노형동', '외도동', '이호동', '도두동'],
    '서귀포시':['송산동', '정방동', '중앙동', '천지동', '효돈동', '영천동', '동홍동', '서홍동', '대륜동', '대천동', '중문동', '예래동'],
    '동제주군':['구좌읍', '남원읍', '성산읍', '우도면', '조천읍', '표선면'],
    '서제주군':['대정읍','안덕면', '애월읍', '한림읍', '추자면','한경면']
}
AREA={}
for key in AREA_GROUP.keys():
    for value in AREA_GROUP[key]:
        AREA[value]=key

def process_search_data(origin_path: str='./data/original', chart_path: str='./data/chart', save_path: str='./data/final'):
    data=pd.read_csv(os.path.join(origin_path,'JEJU_MCT_DATA_v2.csv'),encoding='cp949')
    
    # columns to korean
    with open(os.path.join(origin_path,'korean_columns.json'),'r') as j:
        KOREAN_COLUMNS=json.load(j)
    
    data_dict={}
    columns=data.columns.to_list()
    for column in columns:
        data_dict[KOREAN_COLUMNS[column]]=[]

    print('convert columns to korean...')
    for id in tqdm(data.index):
        target=data.loc[id]
        for column in columns:
            data_dict[KOREAN_COLUMNS[column]].append(target[column])
        
    data_ko=pd.DataFrame(data=data_dict)
    data_ko.to_csv(os.path.join(chart_path,'jeju_mct_data_ko_v1.csv'),encoding='cp949')

    # make administrative district columns and scale some columns
    city_rows=[]
    town_rows=[]
    side_rows=[]
    print('make administrative district columns...')
    for address in tqdm(data_ko['주소']):
        flag=True
        contents=address.split(' ')
        if contents[0]=='':
            city_rows.append(np.nan)
            town_rows.append(np.nan)
            side_rows.append(np.nan)
            continue
        for content in contents:
            if len(content)>1:
                if content[-1]=='시':
                    city_rows.append(content)
                elif content[-1]=='읍':
                    town_rows.append(content)
                elif content[-1]=='면':
                    town_rows.append(content)
                elif content[-1]=='리':
                    side_rows.append(content)
                    flag=False
                    break
                elif content[-1]=='동':
                    town_rows.append(np.nan)
                    side_rows.append(content)
                    flag=False
                    break
        if flag:
            side_rows.append(np.nan)            
    data_ko['시/군']=city_rows
    data_ko['읍/면/구']=town_rows
    data_ko['동/리']=side_rows

    print('scale some columns...')
    for id in tqdm(data.index):
        data_ko.loc[id,'이용건수구간']=data_ko.loc[id]['이용건수구간'].split('_')[1]
        data_ko.loc[id,'이용금액구간']=data_ko.loc[id]['이용금액구간'].split('_')[1]
        data_ko.loc[id,'건당평균이용금액구간']=data_ko.loc[id]['건당평균이용금액구간'].split('_')[1]

    data_ko.to_csv(os.path.join(chart_path,'jeju_mct_data_ko_v2.csv'),encoding='cp949')

    # make region column
    ids=[]
    region=[]
    print('make IDS, region column...')
    for id in tqdm(data_ko.index):
        ids.append(id)
        target=data_ko.loc[id]
        if target['읍/면/구'] is np.nan:
            region.append(target['시/군'])
        else:
            region.append(AREA[target['읍/면/구']])
    data_ko['IDS']=ids
    data_ko['분할구역']=region

    data_ko.to_csv(os.path.join(chart_path,'jeju_mct_data_ko_v3.csv'),encoding='cp949')
    data_ko.to_csv(os.path.join(save_path,'jeju_mct_data_ko_v3.csv'),encoding='cp949')


    