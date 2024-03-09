import pandas as pd

import requests
from bs4 import BeautifulSoup

from datetime import datetime
import time
import re

import sqlite3

# 기사 스크레이핑해서 result_{시간}.csv로 저장하기 
def article_scraping():
    
    date = [] # pd.timestamp 로 변환 필요
    category = [] # em class media_end_categorize_item
    press = [] # em class media_end_linked_more_point
    title = [] # h2 class media_end_head_headline 
    document = [] # article id dic_area
    link = [] 
    
    dates=['20231226', '20231227', '20231228']
    max_page = [23, 25, 24]
    
    for i, day in enumerate(dates): # 날짜별로 반복
        print('\n일시: {}'.format(day))
        
        current_page = 1
        while current_page <= max_page[i]: #페이지별로 반복
            print('\n{}번째 페이지부터 크롤링을 시작합니다.'.format(current_page))
            
            # html 소스 -> source
            url = "https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid2=230&sid1=105&date=" + day + "&page=" + str(current_page)
            web = requests.get(url).content
            source = BeautifulSoup(web, 'html.parser')
    
            # 소스 페이지의 각각의 뉴스 링크 -> urls_list
            urls_list=[]
            for urls in source.find_all('a', {'class':'nclicks(itn.2ndcont)'}):
                if urls.get_text() != '\n\n':
                    urls_list.append(urls.attrs['href'])
            
            # 페이지의 링크들을 들어가 기사 scraping
            for url in urls_list:
                try:
                    headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                    web_news = requests.get(url, headers=headers).content
                    source_news = BeautifulSoup(web_news, 'html.parser')
    
                    d = source_news.find('span', {'class':'media_end_head_info_datestamp_time'}).get_text()
                    d = d.replace(" ","")
                    date1 = d[:11] # 날짜까지 파싱
                    date2 = d[13:] # 시간부분 파싱
                    date3 = (lambda x : 'am' if x == '오전' else 'pm')(date[11:13])
                    date4 = date1 + date2 + date3
                    article_date = pd.Timestamp(date4)
                    article_cat = source_news.find('em', {'class':'media_end_categorize_item'}).get_text()
    
                    article_press = source_news.find('em', {'class':'media_end_linked_more_point'}).get_text()
                    
                    article_title = source_news.find('h2', {'class':'media_end_head_headline'}).get_text()
                    print('\nProcessing article : {}'.format(article_title))
    
                    article_document = source_news.find('article', {'id':'dic_area'}).get_text()
                    article_document = article_document.replace("\n", "")
                    article_document = article_document.replace("// flash 오류를 우회하기 위한 함수 추가function _flash_removeCallback() {}", "")
                    article_document = article_document.replace("동영상 뉴스       ", "")
                    article_document = article_document.replace("동영상 뉴스", "")
                    article_document = article_document.strip()
    
                    article_link = url
                    
                    date.append(article_date)
                    category.append(article_cat)
                    press.append(article_press)
                    title.append(article_title)
                    document.append(article_document)
                    link.append(article_link)
                except:
                    print('*** 다음 링크의 뉴스를 크롤링하는 중 에러가 발생했습니다 : {}'.format(url))
            
            time.sleep(5)
            current_page += 1
    
    article_df = pd.DataFrame({'date':date, 
                               'category':category, 
                               'press':press, 
                               'title':title, 
                               'document':document,
                               'link':link})

    article_df.to_csv('result_{}.csv'.format(datetime.now().strftime('%y%m%d_%H%M')), index=False, encoding='utf-8')
    
    print('\n크롤링이 성공적으로 완료되었습니다!')
    print('\n크롤링 결과를 다음 파일에 저장하였습니다 : {}'.format(datetime.now().strftime('%y%m%d_%H%M')))


# database에 저장
dbpath = "maindb.db" # or "maindb.sqlite"

conn = sqlite3.connect(dbpath)
cur = conn.cursor()

article_df = pd.read_csv('result_231229_2229.csv')

article_df.to_sql('article', conn, index=False)