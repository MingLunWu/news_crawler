from crawler import Crawler_LTN, filter_keyword
import pandas as pd
import json 
import datetime
import os

# Create output folder. (If not exist.)
if not os.path.exists(os.path.join(os.getcwd(), "output")):
    os.makedirs(os.path.join(os.getcwd(), "output"))
# Crawler URL.
YUNLIN = "https://news.ltn.com.tw/ajax/breakingnews/Yunlin/"
POLITIC = "https://news.ltn.com.tw/ajax/breakingnews/politics/"

# Choose which forum to be crawled.
CRAWL_TARGET = [YUNLIN, POLITIC]

# Load Parameter.
with open('config.json') as json_file:
    param = json.load(json_file)

if param['start_date'] in ["today", "None"]:
    start_date = None
else:
    start_date = param["start_date"]

if param['end_date'] in ["today", "None"]:
    end_date = None
else:
    end_date = param["end_date"]

crawler = Crawler_LTN()

result = pd.DataFrame()
for target in CRAWL_TARGET:
    temp = crawler.call_api(target, start_date, end_date)
    result = pd.concat([result, temp], axis=0)

if param["keyword"] is None or len(param["keyword"])==0:
    print("未設定關鍵字！共有{}則新聞".format(result.shape[0]))
else:
    result = filter_keyword(result, param['keyword'])

result.to_csv(os.path.join(os.getcwd(), "output", datetime.datetime.now().strftime("%y_%m_%d_%H_%M")+".csv"))
print("查詢程序完成！已儲存資料！")