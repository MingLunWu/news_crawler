import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json
import pandas as pd

class Crawler_LTN:
    """
        自由電子報
    """
    def __init__(self):
        self.YUNLIN = "https://news.ltn.com.tw/ajax/breakingnews/Yunlin/"
        self.POLITIC = "https://news.ltn.com.tw/ajax/breakingnews/politics/"
    
    def call_api(self, API_URL,start_date=None, end_date=None):
        if start_date is None:
            start_date = datetime(2020,1,1)
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        
        if end_date is None:
            end_date = datetime.today()
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        end_date = end_date.replace(hour=23, minute=59)

        today_docs, api_idx = self.crawl_today(API_URL)
        history_docs = self.crawl_history(API_URL, api_idx+1, start_date, end_date)
        final_df = pd.DataFrame(today_docs + history_docs)
        final_df = final_df.query("date > '{}' & date <= '{}'".format(start_date, end_date))
        return final_df

    # Because the formats of current day and previous day are different.
    # So I define two different crawler functions.
    def crawl_today(self, API_URL):
        docs = list()
        api_idx = 1
        while True:
            r = requests.get(API_URL+str(api_idx))
            data_obj = json.loads(r.text)['data']
            for data in data_obj:
                try: 
                    date = datetime.strptime(data['time'], "%Y-%m-%d %H:%M")
                except ValueError: # 自由時報當日新聞不會有日期，要手動加入.
                    today = datetime.today().strftime("%Y-%m-%d")
                    date = datetime.strptime(today + " " + data['time'], "%Y-%m-%d %H:%M") 
                except TypeError: # 進入此狀況代表已經到歷史資料區了
                    return docs, api_idx

                date = date.strftime("%Y-%m-%d %H:%M")
                title = data['title']
                print("開始瀏覽:{}".format(title))
                print("新聞日期:{}".format(date))
                url = data['url']
                forum = data['type_cn']
                content = self.crawl_content(url)
                docs.append({"title":title, "date": date, "url": url, "content": content, "source":"自由", "forum": forum})
            api_idx += 1
    
    def crawl_history(self, API_URL, api_idx, start_date, end_date):
        docs = list()
        api_idx = api_idx 
        while True:
            r = requests.get(API_URL+str(api_idx))
            data_obj = json.loads(r.text)['data']
            for idx in data_obj.keys():
                try:
                    date = datetime.strptime(data_obj[idx]['time'], "%Y-%m-%d %H:%M")
                except ValueError: # 自由時報當日新聞不會有日期，要手動加入.
                    today = datetime.today().strftime("%Y-%m-%d")
                    date = datetime.strptime(today + " " + data_obj[idx]['time'], "%Y-%m-%d %H:%M") 
                
                if date < start_date:
                    return docs            

                if date > end_date:
                    continue

                date = date.strftime("%Y-%m-%d %H:%M")
                title = data_obj[idx]['title']
                print("開始瀏覽:{}".format(title))
                print("新聞日期:{}".format(date))
                forum = data_obj[idx]['type_cn']
                url = data_obj[idx]['url']
                content = self.crawl_content(url)
                docs.append({"title":title, "date": date, "url": url, "content": content, "source":"自由", "forum": forum})
            api_idx += 1
        

    """ def crawl_docs(self, TOC_URL):
        r = requests.get(TOC_URL)
        origin_html = r.text

        soup = BeautifulSoup(origin_html, "html.parser")
        article_list = soup.find_all("li", {"data-page":1})
        # title_l, date_l, url_l = list(), list(), list()
        
        docs = list()
        
        for article in article_list:
            title = article.find("span", {"class":"title"}).text
            print("搜尋中:{}".format(title))
            date_text = article.find("span", {"class":"time"}).text
            try:
                date = datetime.strptime(date_text, "%Y-%m-%d %H:%M")
            except ValueError: # 自由時報當日新聞不會有日期，要手動加入.
                today = datetime.today().strftime("%Y-%m-%d")
                date = datetime.strptime(today + " " + date_text, "%Y-%m-%d %H:%M") 
            date = date.strftime("%Y-%m-%d %H:%M")
            url = article.find("a")["href"]
            content = self.crawl_content(url)
            docs.append({"title":title, "date": date, "url": url, "content": content})
            
        return docs
     """
    def crawl_content(self, URL):
        r = requests.get(URL)
        origin_html = r.text
        soup = BeautifulSoup(origin_html, "html.parser")
        content = "".join([x.text for x in soup.find_all("p", {"id":None})])
        content = clean_text(content)
        return content

def clean_text(text):
    output = re.sub("\s+", "", text) # Remove Space.

    return output 

def filter_keyword(dataframe, keyword_list):
    keyword_text = "|".join(keyword_list)
    return dataframe[(dataframe.title.str.contains(keyword_text)) | (dataframe.content.str.contains(keyword_text))]

if __name__ == "__main__":
    crawler = Crawler_LTN()
    result = crawler.call_api(crawler.YUNLIN, "2020-06-21", "2020-06-22")
    print("test")       