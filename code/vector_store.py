import os
import json
import torch
import pandas as pd
import numpy as np

import faiss
from langchain.embeddings.base import Embeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore

device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "intfloat/multilingual-e5-large-instruct"
embedding_model = HuggingFaceEmbeddings(model_name=model_name,model_kwargs={'device': device},encode_kwargs={'normalize_embeddings': False},show_progress=True)

def type_vector_store(origin_path: str='./data/original', final_path: str='./data/final', save_path: str='./store'):
    print('make type vector store...')
    data=pd.read_csv(os.path.join(final_path,'jeju_mct_data_ko_v3.csv'),encoding='cp949')
    with open(os.path.join(origin_path,'mct_type_contents_v2.json'),'r') as j:
        page_contents=json.load(j)
    types=data['업종'].value_counts().index
    docs=[Document(metadata={'topic':type},page_content=page_contents[type] ) for type in types]
    vectorstore = FAISS.from_documents(documents=docs, embedding=embedding_model)
    vectorstore.save_local(os.path.join(save_path,'type'))

def range_vector_store(origin_path: str='./data/original', final_path: str='./data/final', save_path: str='./store'):
    print('make range vector store...')
    data=pd.read_csv(os.path.join(final_path,'jeju_mct_data_ko_v3.csv'),encoding='cp949')
    with open(os.path.join(origin_path,'range_contents.json'),'r') as j:
        page_contents=json.load(j)
    auapcs=data['건당평균이용금액구간'].value_counts().index
    docs=[Document(metadata={'topic':auapc},page_content=page_contents[auapc]) for auapc in auapcs]
    vectorstore = FAISS.from_documents(documents=docs, embedding=embedding_model)
    vectorstore.save_local(os.path.join(save_path,'range'))

def address_vector_store(origin_path: str='./data/original', final_path: str='./data/final', save_path: str='./store'):
    print('make address vector store...')
    data=pd.read_csv(os.path.join(final_path,'jeju_mct_data_ko_v3.csv'),encoding='cp949')
    addresses=set()
    for id in data.index:
        city=data.loc[id]['시/군']
        town='' if data.loc[id]['읍/면/구'] is np.nan else data.loc[id]['읍/면/구']
        side=data.loc[id]['동/리']
        if town=='':
            addresses.add(f'{city} {side}')
        else:
            addresses.add(f'{city} {town}')
            addresses.add(f'{city} {town} {side}')
    addresses.add('제주시')
    addresses.add('서귀포시')
    docs=[Document(metadata={'topic':address},page_content=address ) for address in addresses]
    vectorstore = FAISS.from_documents(documents=docs, embedding=embedding_model)
    vectorstore.save_local(os.path.join(save_path,'address'))

def column_vector_store(origin_path: str='./data/original', final_path: str='./data/final', save_path: str='./store'):
    print('make column vector store...')
    with open(os.path.join(origin_path,'column_contents.json'),'r') as j:
        page_contents=json.load(j)
    columns=['기준연월', '가맹점명', '개설일자', '업종', '주소', '이용건수구간', '이용금액구간', '건당평균이용금액구간', '월요일이용건수비중', '화요일이용건수비중', '수요일이용건수비중', '목요일이용건수비중', '금요일이용건수비중', '토요일이용건수비중', '일요일이용건수비중', '5시11시이용건수비중', '12시13시이용건수비중', '14시17시이용건수비중', '18시22시이용건수비중', '23시4시이용건수비중', '현지인이용건수비중', '최근12개월남성회원수비중', '최근12개월여성회원수비중', '최근12개월20대이하회원수비중', '최근12개월30대회원수비중', '최근12개월40대회원수비중', '최근12개월50대회원수비중', '최근12개월60대이상회원수비중']
    docs=[Document(metadata={'topic':column},page_content=page_contents[column] ) for column in columns]
    vectorstore = FAISS.from_documents(documents=docs, embedding=embedding_model)
    vectorstore.save_local(os.path.join(save_path,'columns'))

def attribute_vector_store(origin_path: str='./data/original', final_path: str='./data/final', save_path: str='./store'):
    print('make attribute vector store...')
    with open(os.path.join(origin_path,'mct_flavor.json'),'r') as j:
        page_contents=json.load(j)
    attributes=["기름지다", "고소하다", "구수하다", "든든하다", "진하다", "실하다", "알차다", "짜다", "부드럽다", "담백하다", "신선하다", "얼큰하다", "맵다", "바삭하다", "뜨근하다", "가볍다", "건강하다", "달콤하다", "쓰다", "시다", "정갈하다", "칼칼하다"]
    docs=[Document(metadata={'topic':attribute},page_content=page_contents[attribute] ) for attribute in attributes]
    vectorstore = FAISS.from_documents(documents=docs, embedding=embedding_model)
    vectorstore.save_local(os.path.join(save_path,'attribute'))

def mct_vector_store(origin_path: str='./data/original', chart_path: str='./data/chart', save_path: str='./store'):
    print('make mct vector store...')
    class SimpleVectorEmbeddings(Embeddings):
        def embed_documents(self, texts):
            # 텍스트를 무시하고 벡터를 그대로 반환
            return [np.array(eval(text)) for text in texts]
        
        def embed_query(self, text):
            # 쿼리 텍스트를 벡터로 변환 (여기서는 텍스트가 이미 벡터 형태라고 가정)
            return np.array(eval(text))
        
    data=pd.read_csv(os.path.join(chart_path,'review_to_vector.csv'),encoding='cp949')
    id=data['ID']
    data=data.drop(data.columns[:3],axis=1).to_numpy().astype(np.float32)
    data=np.array(data)
    data = np.ascontiguousarray(data)
    dimension=data.shape[1]
    index=faiss.IndexFlatL2(dimension)
    index.add(data)
    documents = [Document(page_content=str(list(vector)), metadata={"id": id.loc[i]}) for i, vector in enumerate(data)]
    docstore = InMemoryDocstore({str(id.loc[i]): doc for i, doc in enumerate(documents)})
    index_to_docstore_id = {i:id.loc[i] for i in range(data.shape[0])}
    vector_store=FAISS(embedding_function=SimpleVectorEmbeddings(), index=index, docstore=docstore, index_to_docstore_id={i: str(id.loc[i]) for i in range(len(documents))})
    vector_store.save_local(os.path.join(save_path,'mct_vec'))

def make_vector_store():
    type_vector_store()
    range_vector_store()
    address_vector_store()
    column_vector_store()
    attribute_vector_store()
    mct_vector_store()