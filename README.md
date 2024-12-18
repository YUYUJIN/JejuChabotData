# KAIT 주최 및 신한카드 주관 - 2024 빅콘테스트 생성형AI분야 

## Environment Setup
 환경설정입니다.
```
conda create --name preprocessing python=3.10
conda activate preprocessing
pip install -r requirements.txt
```

## Data Preparation
 대회 규정에 따라 원본 데이터 및 전처리가 완료된 데이터들을 공개 대상에서 제외하였습니다. 파일 계층 구조에 따른 파일 설명과 각 코드의 결과로 생성되는 파일들은 아래의 구조 내용과 같습니다.
```
code
├── Crawling_code
│   ├── crawling.py -> crawling 시에 사용한 코드
├── recommend_process.py -> 추천 시스템 데이터 전처리 처리를 위한 코드 모음
├── review_to_vector.py -> 리뷰 데이터 전처리 처리를 위한 코드 모음
├── search_process.py -> 검색 시스템 데이터 전처리 처리를 위한 코드 모음
├── utils.py -> 기타 전처리 처리를 위한 유틸리티 코드 모음
├── vector_store.py -> 벡터 스토어 생성을 위한 코드 모음
data
├── chart -> 전처리 과정 중에 분기점에 해당 되는 데이터 샘플 모음
|   ├── jeju_mct_data_ko_v1.csv -> JEJU_MCT_DATA_v2에서 컬럼명 한글화
|   ├── jeju_mct_data_ko_v2.csv -> 행정 구역 데이터(시/군,읍/면/구,동/리) 생성
|   ├── jeju_mct_data_ko_v3.csv -> IDS(가맹점 ID값), 분할구역(제주시,서귀포시,서제주군,동제주군) 생성
|   ├── keywords_stopfilter.csv -> 불용어 제거
|   ├── keywords_stopfilter_norm.csv -> L2 normalize 진행
|   ├── keywords_stopfilter_norm_sum.csv -> 각 키워드별 벡터 성분의 합
|   ├── keywords_validfilter.csv -> 유효한 300개의 단어만 사용하여 카운트
|   ├── keywords_validfilter_norm.csv -> L2 normalize 진행
|   ├── recommend_data_v1.csv -> 범주형은 최빈값, 수치형은 평균값으로 가맹점 별 대표치 생성
|   ├── recommend_data_v2.csv -> 리뷰 결과를 바탕으로 신한 카드 데이터와 ID, 가맹점명, 주소 키값 설정
|   ├── recommend_data_v3.csv -> 신한 카드 데이터, 리뷰 데이터 최종 병합
|   ├── review_to_keywords.csv -> 리뷰 데이터 키워드 카운트
|   ├── review_to_vector.csv -> 22차원으로 축소된 리뷰 데이터
├── final -> 최종 전처리 과정을 마친 뒤 생성되는 데이터 모음
|   ├── jeju_mct_data_ko_v3.csv -> 최종 검색형 시스템 데이터
|   ├── recommend_data_v3.csv -> 최종 추천형 시스템 데이터
├── original -> 원본 및 기타 커스텀 데이터 모음
|   ├── column_contents.json -> column vector store 생성을 위한 page contents
|   ├── JEJU_MCT_DATA_v2.csv -> 원본 신한 카드 데이터
|   ├── korean_columns.json -> 기존 컬럼들의 한글 변환명 모음
|   ├── mct_flavor.json -> attribute vector store 생성을 위한 page contents
|   ├── mct_type_contents.json -> type vector store 생성을 위한 page contents
|   ├── merged_review.csv -> crawling 결과 중 review 데이터 모음
|   ├── merged_storeinfo.csv -> crawling 결과 중 storeinfo 데이터 모음
|   ├── range_contents.json -> range vector store 생성을 위한 page contents
|   ├── words_to_category.json -> 300차원의 키워드 벡터들을 22차원으로 임베딩 시키기 위해 사전 정의한 커스텀 데이터
```

## Code description
1. search_process  
search_process 코드는 원본 신한 카드 데이터를 기반으로 검색형 데이터 전처리를 진행합니다.  
원본 데이터의 컬럼명을 한글명으로 대체하고, 주소 컬럼을 기반으로 행정 구역 데이터를 생성합니다. 이후 index 값을 기준으로 가맹점의 ID(이후 데이터 병합을 위한 키)와 필터링을 위한 분항구역 데이터를 생성합니다.
2. review_to_vector  
review_to_vector 코드는 리뷰 데이터를 기반으로 추천형 검색을 위한 각 가맹점의 벡터 데이터를 생성합니다.  
리뷰 데이터에서 키워드를 추출하고, 불용어 데이터를 제거합니다. 이후 L2 normalize를 이용해 각 가맹점 벡터들을 단위벡터로 정규화하고, 영향력이 큰 키워드 성분을 추출합니다.  
현재는 전체 키워드 중 300개의 키워드로 한정하여 진행하였고, 이 키워드를 사전에 정의한 word_to_category json의 값을 기반으로 22차원으로 의미론적 축소를 진행하고 L2 normalize를 진행합니다.
3. recommend_process  
recommend_process 코드는 신한 카드 데이터와 리뷰 데이터를 병합하여 추천형 데이터 전처리를 진행합니다.  
신한 카드 데이터를 (가맹점명,주소) 키 값을 기준으로 최빈값, 평균값 등 대표치로 대체합니다. 이후 크롤링한 리뷰 데이터와 병합하여 데이터를 준비합니다.
4. vector_store  
vector_store 코드는 준비한 커스텀 page_contents 데이터들과 최종적으로 생성한 리뷰 벡터 데이터를 사용하여 시스템 구축에 필요한 FAISS 기반 벡터 스토어를 생성합니다.
