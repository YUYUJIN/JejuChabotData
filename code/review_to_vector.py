import os
import re
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
from konlpy.tag import Okt
from collections import Counter

from . import STOPWORDS

def extract_word(text):
    if isinstance(text, str):
        hangul = re.compile('[^가-힣]')
        return hangul.sub(' ', text)
    return ''

def extract_keywords(text, okt):
    if isinstance(text, str):
        tokens = okt.pos(text, stem=True)
        return [word for word, tag in tokens if (tag == 'Adjective') | (tag == 'Noun') | (tag == 'Verb')]
    return []

def review_to_keywords(origin_path: str='./data/original',chart_path: str='./data/chart'):
    storeinfo=pd.read_csv(os.path.join(origin_path,'merged_storeinfo.csv'),encoding='utf-8')
    reviews=pd.read_csv(os.path.join(origin_path,'merged_review.csv'),encoding='utf-8-sig')
    okt=Okt()
    rows=[]
    print('exporting keywords in reviews...')
    for mct in tqdm(reviews['Store ID'].unique()):
        types=' '.join(storeinfo[storeinfo['Store ID']==mct]['업종'])+' '
        review=reviews[reviews['Store ID']==mct]['내용']
        contents=' '
        if len(review)<11:
            for content in review:
                contents+=(types+extract_word(content))
        else:
            for content in review:
                contents+=(types+extract_word(content))
        keywords=extract_keywords(contents,okt)

        keywords_counts = Counter(keywords)
        filtered_keywords = {k: v for k, v in keywords_counts.items() if v > 2}
        top_keywords = Counter(filtered_keywords)

        for key in top_keywords.keys():
            rows.append({'ID': mct,'MCT_NM': ' '.join(reviews[reviews['Store ID']==mct]['MCT_NM'].mode().to_list()), 'Keyword': key, 'Frequency': top_keywords[key]})

    review_to_keyword=pd.DataFrame(data=rows)
    review_to_keyword.to_csv(os.path.join(chart_path,'review_to_keywords.csv'),encoding='cp949')
    return review_to_keyword

def keywords_to_stopwords_filter(review_to_keyword: pd.DataFrame, save_path: str):
    data={'ID':[],'MCT_NM':[],'Keyword':[],'Frequency':[]}
    print('filtering keywords with stopwords...')
    for i in tqdm(review_to_keyword.index):
        target=review_to_keyword.loc[i]
        if target['Keyword'] not in STOPWORDS:
            data['ID'].append(target['ID'])
            data['MCT_NM'].append(target['MCT_NM'])
            data['Keyword'].append(target['Keyword'])
            data['Frequency'].append(target['Frequency'])
    review_to_keywords_filtered=pd.DataFrame(data=data)
    review_to_keywords_filtered.to_csv(save_path, encoding='cp949')
    return review_to_keywords_filtered

def frequency_to_vector(review_to_keyword: pd.DataFrame, save_path: str):
    print('normalizing keyword vectors...')
    for id in tqdm(review_to_keyword['ID'].unique()):
        target=review_to_keyword[review_to_keyword['ID']==id]
        nplist=np.array(target['Frequency'].to_list()).astype('float32')
        norms=np.linalg.norm(nplist)
        nplist/=norms
        for i,w in enumerate(target.index):
            review_to_keyword.loc[w,'Frequency']=nplist[i]
    review_to_keyword.to_csv(save_path,encoding='cp949')
    return review_to_keyword

def vector_to_sum(review_to_keyword: pd.DataFrame, save_path: str):
    words=[]
    freq=[]
    print('calculating sum of vector...')
    for keyword in tqdm(review_to_keyword['Keyword'].unique()):
        words.append(keyword)
        freq.append(review_to_keyword[review_to_keyword['Keyword']==keyword]['Frequency'].sum())
    data={'words':words,'freq':freq}
    keywords_to_count=pd.DataFrame(data=data)
    keywords_to_count.to_csv(save_path,encoding='cp949')

def keywords_to_valid_filter(review_to_keyword: pd.DataFrame,save_path: str, filter_path: str='./data/original/words_to_category.json'):
    with open(filter_path,'r') as j:
        FILTER=json.load(j)
    
    data={'ID':[],'MCT_NM':[],'Keyword':[],'Frequency':[]}
    print('filtering keywords with valid filter...')
    for i in tqdm(review_to_keyword.index):
        target=review_to_keyword.loc[i]
        if FILTER.get(target['Keyword']):
            for n in range(len(FILTER[target['Keyword']])):
                data['ID'].append(target['ID'])
                data['MCT_NM'].append(target['MCT_NM'])
                data['Keyword'].append(FILTER[target['Keyword']][n])
                data['Frequency'].append(target['Frequency'])
    review_to_keywords_filtered=pd.DataFrame(data=data)

    # sum
    data={'ID':[],'MCT_NM':[],'Keyword':[],'Frequency':[]}
    print('calculating sum of keywords...')
    for id in tqdm(review_to_keywords_filtered['ID'].unique()):
        target=review_to_keywords_filtered[review_to_keywords_filtered['ID']==id]
        for word in target['Keyword'].unique():
            data['ID'].append(target['ID'].mode().to_list()[0])
            data['MCT_NM'].append(target['MCT_NM'].mode().to_list()[0])
            data['Keyword'].append(word)
            data['Frequency'].append(target[target['Keyword']==word]['Frequency'].sum())
    review_to_keywords_filtered=pd.DataFrame(data=data)
    review_to_keywords_filtered.to_csv(save_path,encoding='cp949')
    return review_to_keywords_filtered

def keywords_to_vector(review_to_keywords_filtered: pd.DataFrame, save_path: str):
    avaliable_keywords=review_to_keywords_filtered['Keyword'].unique()
    data={'ID':[],'MCT_NM':[]}
    for column in avaliable_keywords:
        data[column]=[]

    print('make keyword vectors...')
    for i,mct in enumerate(tqdm(review_to_keywords_filtered['ID'].unique())):
        data['ID'].append(mct)
        data['MCT_NM'].append(' '.join(review_to_keywords_filtered[review_to_keywords_filtered['ID']==mct]['MCT_NM'].mode().to_list()))
        for column in avaliable_keywords:
            data[column].append(0)
        for value in review_to_keywords_filtered[review_to_keywords_filtered['ID']==mct]['Keyword'].unique():
            if value in avaliable_keywords:
                data[value][i]+=review_to_keywords_filtered[(review_to_keywords_filtered['ID']==mct) & (review_to_keywords_filtered['Keyword']==value)]['Frequency'].sum()
    review_to_vetor=pd.DataFrame(data=data)
    review_to_vetor.to_csv(save_path,encoding='cp949')

def reviews_to_vectors(origin_path: str='./data/original',chart_path: str='./data/chart', save_path: str='./data/final'):
    review_to_keyword=review_to_keywords()
    review_to_keywords_filtered=keywords_to_stopwords_filter(review_to_keyword,os.path.join(chart_path,'keywords_stopfilter.csv'))
    review_to_keywords_filtered=frequency_to_vector(review_to_keywords_filtered,os.path.join(chart_path,'keywords_stopfilter_norm.csv'))
    vector_to_sum(review_to_keywords_filtered,os.path.join(chart_path,'keywords_stopfilter_norm_sum.csv'))

    review_to_keywords_filtered=keywords_to_valid_filter(review_to_keyword,os.path.join(chart_path,'keywords_validfilter.csv'))
    review_to_keywords_filtered=frequency_to_vector(review_to_keywords_filtered,os.path.join(chart_path,'keywords_validfilter_norm.csv'))
    keywords_to_vector(review_to_keywords_filtered,os.path.join(chart_path,'review_to_vector.csv'))