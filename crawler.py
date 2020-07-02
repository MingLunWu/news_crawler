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
        pass
    
    def call_api(self, API_URL,start_date=None, end_date=None):
        if start_date is None:
            start_date = datetime.today()
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        
        start_date = start_date.replace(hour=0, minute=0)
        
        if end_date is None:
            end_date = datetime.today()
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        end_date = end_date.replace(hour=23, minute=59)

        today_docs, api_idx = self.crawl_today(API_URL)
        history_docs = self.crawl_history(API_URL, api_idx+1, start_date, end_date)
        final_df = pd.DataFrame(today_docs + history_docs)
        final_df = final_df.query("date >= '{}' & date <= '{}'".format(start_date, end_date))
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
                url = data['url']
                forum = data['type_cn']
                print("[自由-{}]開始瀏覽:{}".format(forum, title))
                print("[自由-{}]新聞日期:{}".format(forum, date))
                content, reporter = self.crawl_content(url)
                docs.append({"title":title, "date": date, "url": url, "content": content, "source":"自由", "forum": forum, "reporter": reporter})
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
                forum = data_obj[idx]['type_cn']
                print("[自由-{}]開始瀏覽:{}".format(forum, title))
                print("[自由-{}]新聞日期:{}".format(forum, date))
                url = data_obj[idx]['url']
                content, reporter = self.crawl_content(url)
                docs.append({"title":title, "date": date, "url": url, "content": content, "source":"自由", "forum": forum, "reporter":reporter})
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
        query_result = soup.find_all("p", {"id":None})
        content = ""
        for i in query_result[2:]: # First two elements must be "browser alert" and useless tag.
            if "appE1121" in i.get_attribute_list("class"): # If this class appears, means that the article is over. (below is advertisement.)
                break
            else:
                content = content + " " + i.get_text()
        content = clean_text(content)
        try:
            reporter = re.search("(?<=記者).{3}", content).group(0)
        except:
            reporter = None
        return content, reporter

class Crawler_YUNLIN_GOV:
    """ This class use to extract news from 'https://www.yunlin.gov.tw' (Yunlin County Government)
    """
    def __init__(self):
        pass

    def call_api(self, start_date=None, end_date=None):
        result = list()
        if start_date is None or start_date == "today":
            start_date = datetime.today()
            start_date = start_date.replace(hour=0, minute=0)
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        
        if end_date is None or end_date == "today":
            end_date = datetime.today()
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            
        end_date = end_date.replace(hour=23, minute=59)
        
        idx = 1 
        while True:
            r = requests.get("https://www.yunlin.gov.tw/News.aspx?n=1244&sms=9662&page={}&PageSize=200".format(idx))
            soup = BeautifulSoup(r.text, "html.parser")
            all_table = soup.find_all("tr")[1:]
            for a_news in all_table:
                art_type, art_title, _, art_date = [x.text for x in a_news.find_all("td")]
                art_url = "https://www.yunlin.gov.tw/" + a_news.find("a").get("href")
                # Convert Taiwan Year to Western Year.
                temp = art_date.split("-")
                temp[0] = str(int(temp[0]) + 1911)
                art_date = "-".join(temp)
                art_date = datetime.strptime(art_date, "%Y-%m-%d")
                art_date = art_date.replace(hour=23, minute=58)
                print("[縣府-{}]開始瀏覽:{}".format(art_type, art_title))
                print("[縣府-{}]新聞日期:{}".format(art_type, art_date))
                if art_date < start_date:
                    if len(result) > 0:
                        final_df = pd.DataFrame(result)
                        final_df = final_df.query("date >= '{}' & date <= '{}'".format(datetime.strftime(start_date,"%Y-%m-%d"), datetime.strftime(end_date,"%Y-%m-%d")))
                    else:
                        final_df = pd.DataFrame(columns=["title", "date", "url", "content", "source", "forum", "reporter"])
                    return final_df
                elif start_date <= art_date < end_date:
                    art_content, reporter = self.crawl_content(art_url)
                    result.append({"title":art_title, "date": datetime.strftime(art_date,"%Y-%m-%d"), "url": art_url, "content": art_content, "source":"雲林縣政府", "forum": art_type, "reporter": reporter})
            idx += 1

    def crawl_content(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        reporter_html = soup.find("div",{"id":"CCMS_Content"}).select("li span")[0].text
        reporter = re.search("(?<=發布單位：).*", reporter_html).group(0)
        content = soup.find_all("div", {"class":"p"})[1].text
        content = clean_text(content)
        return content, reporter

class Crawler_ChinaTime():
    def __init__(self):
        super().__init__()
    
    def call_api(self, start_date=None, end_date=None):
        result = list()
        if start_date is None or start_date == "today":
            start_date = datetime.today()
            start_date = start_date.replace(hour=0, minute=0)
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        
        if end_date is None or end_date == "today":
            end_date = datetime.today()
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            
        end_date = end_date.replace(hour=23, minute=59)
        
        idx = 1
        while idx<=10:
            url = "https://www.chinatimes.com/politic/total?page={}&chdtv".format(idx)
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            all_articles = soup.find_all("div", {"class": "articlebox-compact"})
            for article in all_articles:
                art_title = article.find("h3", {"class":"title"}).text
                art_date = datetime.strptime(article.find("time").get("datetime"), "%Y-%m-%d %H:%M")
                art_url = "https://www.chinatimes.com"+article.find("h3", {"class":"title"}).find("a").get("href")
                print("[中時-政治]開始瀏覽:{}".format(art_title))
                print("[中時-政治]新聞日期:{}".format(art_date))
                if art_date < start_date:
                    if len(result) > 0:
                        final_df = pd.DataFrame(result)
                        final_df = final_df.query("date >= '{}' & date <= '{}'".format(start_date, end_date))
                    else:
                        final_df = pd.DataFrame(columns=["title", "date", "url", "content", "source", "forum", "reporter"])
                    return final_df
                elif start_date <= art_date < end_date:
                    art_content, reporter = self.crawl_content(art_url)
                    result.append({"title":art_title, "date": datetime.strftime(art_date,"%Y-%m-%d %H:%M"), "url": art_url, "content": art_content, "source":"中時電子報", "forum": "政治", "reporter": reporter})
            idx += 1
            
        if len(result) > 0:
            final_df = pd.DataFrame(result)
            # final_df = final_df.query("date >= '{}' & date <= '{}'".format(datetime.strftime(start_date,"%Y-%m-%d"), datetime.strftime(end_date,"%Y-%m-%d")))
        else:
            final_df = pd.DataFrame(columns=["title", "date", "url", "content", "source", "forum", "reporter"])
        return final_df

    def crawl_content(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        content = clean_text(soup.find("div", {"class":"article-body"}).text)
        reporter = clean_text(soup.find("div", {"class":"author"}).text)

        return content, reporter

def clean_text(text):
    output = re.sub("\s+", "", text) # Remove Space.

    return output 

def filter_keyword(dataframe, keyword_list):
    keyword_text = "|".join(keyword_list)
    filter_df = dataframe[(dataframe.title.str.contains(keyword_text)) | (dataframe.content.str.contains(keyword_text))]
    print("已瀏覽日期區間所有{}則新聞, 符合關鍵字的共有{}則新聞！".format(dataframe.shape[0], filter_df.shape[0]))
    return filter_df

if __name__ == "__main__":
    crawler = Crawler_ChinaTime()
    result = crawler.call_api("today","today")
    print("result")