import os
import json
import pandas as pd
from tqdm import tqdm

RANGE_GROUP=['이용건수구간', '이용금액구간', '건당평균이용금액구간']
NUMBER_GROUP=['월요일이용건수비중', '화요일이용건수비중', '수요일이용건수비중', '목요일이용건수비중', '금요일이용건수비중', '토요일이용건수비중', '일요일이용건수비중', 
              '5시11시이용건수비중', '12시13시이용건수비중', '14시17시이용건수비중', '18시22시이용건수비중', '23시4시이용건수비중', '현지인이용건수비중', 
              '최근12개월남성회원수비중', '최근12개월여성회원수비중', '최근12개월20대이하회원수비중', '최근12개월30대회원수비중', '최근12개월40대회원수비중', 
              '최근12개월50대회원수비중', '최근12개월60대이상회원수비중']

def process_recommend_data(origin_path: str='./data/original', chart_path: str='./data/chart', save_path: str='./data/final'):
    data=pd.read_csv(os.path.join(chart_path,'jeju_mct_data_ko_v3.csv'),encoding='cp949')
    
    data_dict={}
    columns=data.columns.to_list()
    del columns[0] # 인덱스 삭제
    del columns[0] # 기준연월삭제
    del columns[1] # 개설일자 삭제
    for column in columns:
        data_dict[column]=[]

    none_duplicates=data.drop_duplicates(['가맹점명','주소'])[['가맹점명','주소']]
    print('mean data...')
    for id in tqdm(none_duplicates.index):
        mct_nm,addr=none_duplicates.loc[id]
        targets=data[(data['가맹점명']==mct_nm)&(data['주소']==addr)]

        data_dict['가맹점명'].append(mct_nm)
        data_dict['주소'].append(addr)
        data_dict['업종'].append(targets['업종'].to_list()[0])
        data_dict['시/군'].append(targets['시/군'].to_list()[0])
        data_dict['읍/면/구'].append(targets['읍/면/구'].to_list()[0])
        data_dict['동/리'].append(targets['동/리'].to_list()[0])
        data_dict['IDS'].append(targets['IDS'].to_list()[0])
        data_dict['분할구역'].append(targets['분할구역'].to_list()[0])

        for column in RANGE_GROUP:
            contents=targets[column].mode().to_list()
            if len(contents)>1:
                data_dict[column].append(', '.join(contents))
            else:
                data_dict[column].append(contents[0])

        for column in NUMBER_GROUP:
            data_dict[column].append(targets[column].mean())

    data_mean=pd.DataFrame(data=data_dict)
    data_mean.to_csv(os.path.join(chart_path,'recommend_data_v1.csv'),encoding='cp949')

    data_vec=pd.read_csv(os.path.join(chart_path,'review_to_vector.csv'),encoding='cp949')
    data_info=pd.read_csv(os.path.join(origin_path,'merged_storeinfo.csv'),encoding='utf-8-sig')

    valid_ids=data_vec['ID'].unique()
    data_info=data_info[data_info['Store ID'].isin(valid_ids)]
    data_info['IDS']=data_info['Store ID']
    data_info=data_info.drop(['Store ID'],axis=1)
    data_info.to_csv(os.path.join(chart_path,'recommend_data_v2.csv'),encoding='utf-8-sig')

    data_dict={}
    INFO_COLUMNS=['IDS','별점','운영시간','번호','부가설명','링크','메뉴','좋은점','리뷰 갯수']
    MEAN_COLUMNS=['가맹점명','업종','주소','이용건수구간','이용금액구간','건당평균이용금액구간','월요일이용건수비중','화요일이용건수비중','수요일이용건수비중','목요일이용건수비중','금요일이용건수비중','토요일이용건수비중','일요일이용건수비중',
                  '5시11시이용건수비중','12시13시이용건수비중','14시17시이용건수비중','18시22시이용건수비중','23시4시이용건수비중','현지인이용건수비중','최근12개월남성회원수비중','최근12개월여성회원수비중','최근12개월20대이하회원수비중',
                  '최근12개월30대회원수비중','최근12개월40대회원수비중','최근12개월50대회원수비중','최근12개월60대이상회원수비중','시/군','읍/면/구','동/리','분할구역']
    for column in ['IDS','가맹점명','업종','주소']:
        data_dict[column]=[]
    for column in INFO_COLUMNS:
        data_dict[column]=[]
    for column in MEAN_COLUMNS:
        data_dict[column]=[]
    

    none_duplicates=data_info.drop_duplicates(['MCT_NM','ADDR'])[['MCT_NM','ADDR']]
    print('merging store info data and mean data...')
    for id in tqdm(none_duplicates.index):
        mct_nm,addr=none_duplicates.loc[id]
        info=data_info[(data_info['MCT_NM']==mct_nm)&(data_info['ADDR']==addr)]
        mean=data_mean[(data_mean['가맹점명']==mct_nm)&(data_mean['주소']==addr)]

        for column in MEAN_COLUMNS:
            data_dict[column].append(mean[column].to_list()[0])
        for column in INFO_COLUMNS:
            data_dict[column].append(info[column].to_list()[0])
    data_new=pd.DataFrame(data=data_dict)
    data_new.to_csv(os.path.join(chart_path,'recommend_data_v3.csv'),encoding='utf-8-sig')
    data_new.to_csv(os.path.join(save_path,'recommend_data_v3.csv'),encoding='utf-8-sig')