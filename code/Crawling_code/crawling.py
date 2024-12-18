"""
How to Use
1. 터미널에 라이브러리 설치
    pip install beautifulsoup4
    pip install pandas
    pip install selenium
    pip install webdriver_manager
    pip install openpyxl
    pip install lxml
2. review.csv / storeinfo.csv 파일로 저장됨
"""

from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from openpyxl import Workbook
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException
import time



# Webdriver 설정
def setup_webdriver():
    options = webdriver.ChromeOptions()
    prefs = {
    "profile.managed_default_content_settings.images": 2  # 이미지 로딩 비활성화(속도 향상)
    }   
    options.add_experimental_option("prefs", prefs)
    options.add_argument('window-size=1920x1080')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print("웹드라이버 설정 완료")
    return driver



# searchIframe 전환
# 검색 결과를 포함하는 iframe으로 전환하는 함수
def switch_to_searchiframe():
    try:
        driver.switch_to.default_content() # 기본 프레임으로 돌아가기
        iframe = driver.find_element(By.XPATH, '//*[@id="searchIframe"]')
        driver.switch_to.frame(iframe) # searchIframe으로 전환
        print("searchIframe으로 전환 완료")
    except Exception as e:
        print(f"searchIframe 전환 오류: {e}")
        raise



# entryIframe 전환
# 상세 정보를 포함하는 iframe으로 전환하는 함수
def switch_to_entryiframe():
    try:
        driver.switch_to.default_content() # 기본 프레임으로 돌아가기
        iframe = driver.find_element(By.XPATH, '//*[@id="entryIframe"]')
        driver.switch_to.frame(iframe) # entryIframe으로 전환
        print("entryIframe으로 전환 완료")
    except Exception as e:
        print(f"entryIframe 전환 오류: {e}")
        raise



# 팝업창 닫기
def close_popup():
    try:
        driver.switch_to.default_content()
        try: # 팝업창1 (button 타입)
            popup_close_button1 = WebDriverWait(driver, 0.05).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'body > div.sc-1s1ma4y.cEChVv > div > button'))
            )
            popup_close_button1.click()
            print("[팝업창 제거 완료_1]")
            time.sleep(0.5)
        except (TimeoutException, NoSuchElementException):
            print("[팝업창 없음_1]")
        try: # 팝업창2 (button.btn_close 타입)
            popup_close_button2 = WebDriverWait(driver, 0.05).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'body > div.sc-1s1ma4y.cEChVv > div > button.btn_close'))
            )
            popup_close_button2.click()
            print("[팝업창 제거 완료_2]")
            time.sleep(0.5)
        except (TimeoutException, NoSuchElementException):
            print("[팝업창 없음_2]")
    except (TimeoutException, NoSuchElementException):
        print("팝업창 없음")
    finally:
        try:
            switch_to_entryiframe() # 팝업 제거 후 entryIframe으로 전환 시도
            print("iframe으로 전환 완료")
        except NoSuchElementException:
            print("iframe 없음")



# 상호명과 새 주소로 가게를 검색하고, 첫 번째 결과를 클릭
def search_store(store_name, new_addr):
    try:
        search_query = f"{store_name} {new_addr}"  # 상호명과 새 주소로 검색
        search_url = f"https://map.naver.com/v5/search/{search_query}"
        print(f"검색 : {search_query}")
        driver.get(search_url)
        time.sleep(2)
        switch_to_searchiframe()
        first_result = WebDriverWait(driver,5).until( # 첫 번째 검색 결과 가게 클릭
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#_pcmap_list_scroll_container > ul > li:nth-child(1) > div'))
        )
        try:
            first_result.click()
            print(f"첫 가게 클릭 완료: {store_name}")
        except ElementClickInterceptedException:
            print(f"이미 가게가 선택됨")
        switch_to_entryiframe()
        print(f"entryIframe으로 전환 완료")
        
    except TimeoutException:
        print(f"'{store_name}'의 검색 결과를 찾을 수 없습니다.")
        return False
    except Exception as e:
        print(f"검색 중 오류 발생: {e}")
        return False
    return True



# 가게의 홈 탭 정보 크롤링
def crawl_home():
    try:
        print("[홈 탭 크롤링]")

        # 가게명
        try:
            store_name = (driver.find_element(By.CSS_SELECTOR, '#_title > div > span.GHAhO')).text
            print(f"가게명 크롤링 완료 : {store_name}")
        except Exception as e:
            store_name = 'N/A'
            print(f"가게명 크롤링 실패: {e}")

        # 주소
        try:
            address = driver.find_element(By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(5) > div > div:nth-child(2) > div.place_section_content > div > div.O8qbU.tQY7D > div > a > span.LDgIH').text
            print(f"주소 크롤링 완료: {address}")
        except Exception as e:
            address = 'N/A'
            print(f"주소 크롤링 실패: {e}")

        # 업종
        try:
            category = driver.find_element(By.CSS_SELECTOR, '#_title > div > span.lnJFt').text
            print(f"업종 크롤링 완료: {category}")
        except Exception as e:
            category = 'N/A'
            print(f"업종 크롤링 실패: {e}")

        #영업시간
        try:
            operating_hours_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(5) > div > div:nth-child(2) > div.place_section_content > div > div.O8qbU.pSavy > div > a > div > div > span'))
            )
            operating_hours_button.click()
            time.sleep(0.5)
        except TimeoutException:
            print("영업시간 더보기 없음")

        try:
            operating_hours_element = driver.find_element(By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(5) > div > div:nth-child(2) > div.place_section_content > div > div.O8qbU.pSavy > div > a')
            operating_hours_html = operating_hours_element.get_attribute('outerHTML')
            soup = BeautifulSoup(operating_hours_html, 'lxml')
            for div in soup.select('div.w9QyJ.vI8SM'):
                div.decompose()
            operating_hours = soup.get_text(separator="\n").strip()
            print(f"영업시간 크롤링 완료: {operating_hours}")
        except Exception as e:
            operating_hours = 'N/A'
            print(f"영업시간 크롤링 실패: {e}")

        # 전화번호
        try:
            phone = driver.find_element(By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(5) > div > div:nth-child(2) > div.place_section_content > div > div.O8qbU.nbXkr > div > span.xlx7Q').text
            print(f"전화번호 크롤링 완료: {phone}")
        except Exception as e:
            phone = 'N/A'
            print(f"전화번호 크롤링 실패: {e}")

        # 가게 부가 설명
        try:
            description = driver.find_element(By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(5) > div > div:nth-child(2) > div.place_section_content > div > div.O8qbU.Uv6Eo > div > div').text
            print(f"부가 설명 크롤링 완료: {description}")
        except Exception as e:
            description = 'N/A'
            print(f"부가 설명 크롤링 실패: {e}")

        # 링크
        try:
            page_link = driver.current_url
            print(f"링크 크롤링 완료: {page_link}")
        except Exception as e:
            page_link = 'N/A'
            print(f"링크 크롤링 실패: {e}")

        return store_name, address, category, operating_hours, phone, description, page_link
    except Exception as e:
        print(f"홈 탭 크롤링 중 오류 발생: {e}")
        return None



# 가게의 메뉴 탭 크롤링
def crawl_menu():
    try:
        print("[메뉴 탭 크롤링]")

        # 메뉴 탭 클릭
        for i in range(1, 10):
            menu_tab = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f'#app-root > div > div > div > div.place_fixed_maintab > div > div > div > div > a:nth-child({i})'))
            )
            if menu_tab.text == "메뉴":
                menu_tab.click()
                print("메뉴 탭 클릭 완료")
                time.sleep(0.5)
                break

        # 메뉴에서 더보기 클릭
        try:
            more_button = driver.find_element(By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(6) > div:nth-child(2) > div.place_section.no_margin > div.NSTUp > div > a > span')
            more_button.click()
            time.sleep(0.5)

        except NoSuchElementException:
            pass

        possible_name_classes = ['lPzHi', 'tit']  # 메뉴 이름이 있을 수 있는 클래스
        possible_price_classes = ['GXS1X', 'price']  # 메뉴 가격이 있을 수 있는 클래스

        # 메뉴 리스트 확인
        menu_list = []

        # 메뉴 이름 찾기
        for name_class in possible_name_classes:
            item_names = driver.find_elements(By.CLASS_NAME, name_class)  # 메뉴 이름 찾기 시도
            if item_names:
                break  # 유효한 클래스가 발견되면 중단

        # 메뉴 가격 찾기
        for price_class in possible_price_classes:
            item_prices = driver.find_elements(By.CLASS_NAME, price_class)  # 메뉴 가격 찾기 시도
            if item_prices:
                break  # 유효한 클래스가 발견되면 중단

        # 메뉴 정보 수집
        for i in range(len(item_names)):
            try:
                menu_name = item_names[i].text if i < len(item_names) else 'N/A'  # 메뉴 이름 가져오기
                menu_price = item_prices[i].text if i < len(item_prices) else 'N/A'  # 메뉴 가격 가져오기
                menu_list.append(f"[{menu_name}|{menu_price}]")
                print(f"메뉴 항목 크롤링: [{menu_name}|{menu_price}]")
            except Exception as e:
                print(f"메뉴 크롤링 오류: {e}")
                continue

        return ', '.join(menu_list) if menu_list else 'N/A'
    except Exception as e:
        print(f"메뉴 크롤링 중 오류 발생: {e}")
        return '메뉴 크롤링 오류'



# 가게의 리뷰 탭 정보 크롤링
def crawl_review():
    try:
        print("[리뷰 탭 크롤링]")

        # 리뷰 탭 클릭
        for i in range(1, 10):
            review_tab = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f'#app-root > div > div > div > div.place_fixed_maintab > div > div > div > div > a:nth-child({i})'))
            )
            if review_tab.text == "리뷰":
                review_tab.click()
                print("리뷰 탭 클릭 완료")
                time.sleep(0.5)
                break

        time.sleep(0.5)
        review_list = []
        review_count = 0
        review_positives = []
        review_star = ''

        # 별점 추출
        try:
            review_star = driver.find_element(By.CSS_SELECTOR, '#app-root > div > div > div > div.place_section.no_margin.OP4V8 > div.zD5Nm.undefined > div.dAsGb > span.PXMot.LXIwF').text
            print(f"별점 크롤링 완료: {review_star}")
        except NoSuchElementException:
            print("별점을 찾을 수 없습니다.")
            review_star = 'N/A'
        
        # 좋은점 더보기 버튼 클릭
        try:
            positives_more_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(6) > div:nth-child(3) > div.place_section.no_margin.ySHNE > div > div > div.mrSZf > a > svg'))
            )                                                       
            positives_more_button.click()
            print("좋은점 더보기 버튼 클릭 완료")
            time.sleep(0.5)
        except (TimeoutException, NoSuchElementException) as e:
            print(f"좋은점 더보기 버튼 클릭 실패: {e}")
            
        # 좋은 점 추출
        try:
            for i in range(1, 11): 
                positive_content_selector = f'#app-root > div > div > div > div:nth-child(6) > div:nth-child(3) > div.place_section.no_margin.ySHNE > div > div > div.mrSZf > ul > li:nth-child({i}) > div.vfTO3 > span.t3JSf'
                positive_count_selector = f'#app-root > div > div > div > div:nth-child(6) > div:nth-child(3) > div.place_section.no_margin.ySHNE > div > div > div.mrSZf > ul > li:nth-child({i}) > div.vfTO3 > span.CUoLy'
                positive_content_element = driver.find_element(By.CSS_SELECTOR, positive_content_selector)
                positive_content = positive_content_element.text.strip()
                positive_count_element = driver.find_element(By.CSS_SELECTOR, positive_count_selector)
                positive_count = positive_count_element.text.replace('이 키워드를 선택한 인원\n', '').strip()  # 인원 수에서 불필요한 부분 제거

                review_positives.append(f"[{positive_content}|{positive_count}]")

            positives_text = ', '.join(review_positives) if review_positives else 'N/A'
            print(f"좋은점 크롤링 완료: {positives_text}")
        except NoSuchElementException:
            print("좋은점을 찾을 수 없습니다.")
            positives_text = 'N/A'

        # 더보기 버튼 최대 9회 클릭 (크롤링 정보 갯수 제한)
        for i in range(1, 10):
            # close_popup()
            try:
                more_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="app-root"]/div/div/div/div[6]/div[3]/div[3]/div[2]/div/a/span'))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
                driver.execute_script("arguments[0].click();", more_button)
                time.sleep(0.5)
                print(f"{i}번째 더보기 클릭 완료")
            except TimeoutException:
                print("더보기 버튼 없음")
                break

        # HTML 파싱
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        reviews = soup.select('li.pui__X35jYm.EjjAW')


        for index, review in enumerate(reviews):

            # 새로 로드된 HTML로부터 리뷰 정보를 추출
            updated_html = driver.page_source
            updated_soup = BeautifulSoup(updated_html, 'lxml')
            review_element = updated_soup.select_one(f'li.pui__X35jYm.EjjAW:nth-child({index + 1})')

            # 날짜 추출
            date_elements = review_element.select('div.pui__QKE5Pr > span.pui__gfuUIT > time')
            date = date_elements[0].text if date_elements else 'N/A'

            # 방문 목적 추출
            purpose = review_element.select_one('div.pui__-0Ter1 > a > span:nth-child(3)')
            purpose = purpose.text if purpose else 'N/A'

            # 동행자 추출
            companion = review_element.select_one('div.pui__-0Ter1 > a > span:nth-child(4)')
            companion = companion.text if companion else 'N/A'
            
            # 재방문 여부 추출
            revisit_span = review_element.select('div.pui__QKE5Pr > span.pui__gfuUIT')
            revisit = revisit_span[1].text if len(revisit_span) > 1 else 'N/A'

            # 리뷰 내용 추출
            content = review_element.select_one('div.pui__vn15t2 > a.pui__xtsQN-')
            content = content.text if content else 'N/A'

            # 각 리뷰 데이터를 리스트에 추가
            review_list.append([date, purpose, companion, revisit, content])
            print(f"리뷰 크롤링: [{date}|{purpose}|{companion}|{revisit}|{content}]")
            review_count += 1
            time.sleep(0.05)

        print(f"{review_count}개의 리뷰 크롤링 완료")
        return review_star, review_positives, review_list, review_count

    except Exception as e:
        print(f"리뷰 크롤링 중 오류 발생: {e}")  
        return '리뷰 크롤링 오류'



# Webdriver 및 데이터 파일 준비
driver = setup_webdriver()
csv_file = 'new_address_v1.csv'
df = pd.read_csv(csv_file, encoding="cp949")
store_names = df['MCT_NM'].tolist()
new_addrs = df['NEW_ADDR'].tolist()
print(f"{len(store_names)}개의 가게")

# 엑셀 파일 준비
xlsx = Workbook()
list_sheet = xlsx.active
list_sheet.title = 'output'
list_sheet.append(['ID', '가게명', '주소', '업종', '별점', '운영시간', '번호', '부가설명', '링크', '메뉴', '좋은점', '리뷰 갯수'])

# 가게별 크롤링 실행
storeinfo_file_created = False
review_file_created = False
storeinfo_file = "storeinfo.csv"
review_file = "review.csv"
id_counter = 2 #컬럼명 고려

# 가게별 크롤링 실행
for store_name, new_addr in zip(store_names, new_addrs):
    try:
        if pd.isna(store_name):
            print(f"건너뜀: {new_addr}")
            id_counter += 1
            continue
        print(f"크롤링 중: {store_name}, {new_addr}")
        
        if search_store(store_name, new_addr):  # 상호명과 새 주소로 검색
            home_name, home_address, home_category, home_operating_hours, home_phone, home_description, home_link = crawl_home()
            menu_data = crawl_menu()
            review_star, review_positive, review_list, review_count = crawl_review()

            # storeinfo.csv 저장
            if home_name:
                storeinfo_df = pd.DataFrame([{
                    'ID': id_counter,
                    '가게명': home_name,
                    '주소': home_address,
                    '업종': home_category,
                    '별점': review_star, 
                    '운영시간': home_operating_hours,
                    '번호': home_phone,
                    '부가설명': home_description,
                    '링크': home_link,
                    '메뉴': menu_data,
                    '좋은점': review_positive,
                    '리뷰 갯수': review_count 
                }])
                
                # 첫 가게의 경우 파일 생성
                if not storeinfo_file_created:
                    storeinfo_df.to_csv(storeinfo_file, index=False, encoding="utf-8-sig")
                    storeinfo_file_created = True
                else:
                    storeinfo_df.to_csv(storeinfo_file, mode='a', header=False, index=False, encoding="utf-8-sig")
                print(f"[storeinfo.csv에 데이터 추가 완료: {store_name}]")

                # review.csv 저장
                if review_count > 0:
                    review_list_with_info = [[id_counter, home_name, home_address] + review for review in review_list]
                    review_df = pd.DataFrame(review_list_with_info, columns=['ID', '가게명', '주소', '날짜', '목적', '동행자', '재방문', '내용'])

                    if not review_file_created:
                        review_df.to_csv(review_file, index=False, encoding="utf-8-sig")
                        review_file_created = True
                    else:
                        review_df.to_csv(review_file, mode='a', header=False, index=False, encoding="utf-8-sig")
                    print(f"[review.csv에 데이터 추가 완료: {store_name}]")
                else:
                    print(f"리뷰 없음 처리: {store_name}")

            id_counter +=1
        
        else:
            # 폐업 처리
            storeinfo_df = pd.DataFrame([{
                'ID': id_counter,
                '가게명': store_name,
                '주소': '폐업',
                '업종': '폐업',
                '별점': '폐업',
                '운영시간': '폐업',
                '번호': '폐업',
                '부가설명': '폐업',
                '링크': '폐업',
                '메뉴': '폐업',
                '좋은점': '폐업',
                '리뷰 갯수': '폐업'
            }])

            review_df = pd.DataFrame([{
                'ID': id_counter,
                '가게명': store_name,
                '주소': '폐업',
                '날짜': '폐업',
                '목적': '폐업',
                '동행자': '폐업',
                '별점': '폐업',
                '좋은점': '폐업',
                '재방문': '폐업',
                '내용': '폐업'
            }])
            
            # 폐업 데이터를 storeinfo.csv와 review.csv에 추가
            if not storeinfo_file_created:
                storeinfo_df.to_csv(storeinfo_file, index=False, encoding="utf-8-sig")
                storeinfo_file_created = True
            else:
                storeinfo_df.to_csv(storeinfo_file, mode='a', header=False, index=False, encoding="utf-8-sig")
            
            if not review_file_created:
                review_df.to_csv(review_file, index=False, encoding="utf-8-sig")
                review_file_created = True
            else:
                review_df.to_csv(review_file, mode='a', header=False, index=False, encoding="utf-8-sig")
            
            print(f"[폐업 처리] : {store_name}")

            id_counter += 1

    
    except Exception as e:
        # 에러 발생 시 처리
        storeinfo_df = pd.DataFrame([{
            'ID': id_counter,
            '가게명': store_name,
            '주소': '에러',
            '업종': '에러',
            '별점': '에러',
            '운영시간': '에러',
            '번호': '에러',
            '부가설명': '에러',
            '링크': '에러',
            '메뉴': '에러',
            '좋은점': '에러',
            '리뷰 갯수': '에러'
        }])

        review_df = pd.DataFrame([{
            'ID': id_counter,
            '가게명': store_name,
            '주소': '에러',
            '날짜': '에러',
            '목적': '에러',
            '동행자': '에러',
            '별점': '에러',
            '좋은점': '에러',
            '재방문': '에러',
            '내용': '에러'
        }])

        # 에러 데이터를 storeinfo.csv와 review.csv에 추가
        if not storeinfo_file_created:
            storeinfo_df.to_csv(storeinfo_file, index=False, encoding="utf-8-sig")
            storeinfo_file_created = True
        else:
            storeinfo_df.to_csv(storeinfo_file, mode='a', header=False, index=False, encoding="utf-8-sig")

        if not review_file_created:
            review_df.to_csv(review_file, index=False, encoding="utf-8-sig")
            review_file_created = True
        else:
            review_df.to_csv(review_file, mode='a', header=False, index=False, encoding="utf-8-sig")
        
        print(f"[오류 발생 : {e}] : {store_name}")

        id_counter += 1


print("크롤링 완료 및 파일 저장 완료.")

# 이후 Key.csv 파일을 통해 CRAWLED_NM(* 가게명), CRAWLED_ADDR(* 주소)를 기준으로 MCT_NM, ADDR, NEW_ADDR 병합


storeinfo_df = pd.read_csv("storeinfo.csv", encoding="utf-8-sig")
review_df = pd.read_csv("review.csv", encoding="utf-8-sig")
key_df = pd.read_csv("Key.csv", encoding="utf-8-sig")

storeinfo_df.rename(columns={'가게명': 'CRAWLED_NM', '주소': 'CRAWLED_ADDR'}, inplace=True)
review_df.rename(columns={'가게명': 'CRAWLED_NM', '주소': 'CRAWLED_ADDR'}, inplace=True)

merged_storeinfo_df = pd.merge(storeinfo_df, key_df[['MCT_NM', 'ADDR', 'NEW_ADDR', 'CRAWLED_NM', 'CRAWLED_ADDR']], 
                               on=['CRAWLED_NM', 'CRAWLED_ADDR'], 
                               how='inner')

merged_review_df = pd.merge(review_df, key_df[['MCT_NM', 'ADDR', 'NEW_ADDR', 'CRAWLED_NM', 'CRAWLED_ADDR']], 
                            on=['CRAWLED_NM', 'CRAWLED_ADDR'], 
                            how='inner')

merged_storeinfo_df.rename(columns={'CRAWLED_NM': '가게명', 'CRAWLED_ADDR': '주소'}, inplace=True)
merged_review_df.rename(columns={'CRAWLED_NM': '가게명', 'CRAWLED_ADDR': '주소'}, inplace=True)

merged_storeinfo_df.to_csv("merged_storeinfo.csv", index=False, encoding="utf-8-sig")
merged_review_df.to_csv("merged_review.csv", index=False, encoding="utf-8-sig")

print("병합 완료: merged_storeinfo.csv와 merged_review.csv 파일이 생성되었습니다.")