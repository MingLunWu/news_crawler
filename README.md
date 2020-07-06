# News Extractor - Politic and Yunlin Domain

This tool is a simple public opinion system that used for extracting daily news (Traditional Chinese) from different sources in Taiwan, include:
- [x] [LTN - Politics + Yunlin Forum](https://www.ltn.com.tw) (Done)
- [x] [Yunlin County Government](https://www.yunlin.gov.tw/News.aspx?n=1244&sms=9662) (Done)
- [x] [ChinaTimes - Politics Forum](https://www.chinatimes.com/politic/total?page=1&chdtv) (Done)
- [ ] UDN (TBD)
- [ ] EBC (TBD)
- [ ] Apple Daily (TBD)

## Installation
### with conda 
```bash
git clone https://github.com/MingLunWu/news_crawler.git
cd news_crawler
conda env create -f environment.yml
```

## Usage 
### Set config.json

In order to filter news by keyword or date range, please set your own condition as needed.

```json
{
    "keyword":["雲林","雲縣"],  
    "start_date": "None", 
    "end_date": "None" 
}
```
+ **keyword** : To filter the news that contains at least one keyword in the title or content field.
+ **start_date** : Define the time interval to retrieve news. (format: `yyyy-mm-dd`, 2020-06-20, "none" and "today" means today.)
+ **end_date**: Define the time interval to retrieve news. (format: `yyyy-mm-dd`, 2020-06-20, "none" and "today" means today.)

### Run the script.
Make sure the virtual environment have already been created through conda command and `config.json` has been set.

```bash
bash start.sh
```

After the script executed, the news that match your conditions will be saved as a csv file and written to your project's `output` folder.

**Example output:** 

|   title   |       date       |                            url                           |     content     | source | forum | reporter |
|:---------:|:----------------:|:--------------------------------------------------------:|:---------------:|:------:|:-----:|:--------:|
| 新聞標題1 | 2020-06-20 13:00 | https://news.ltn.com.tw/news/Yunlin/breakingnews/3214390 |   news content  |  自由  |  生活 |   name1  |
| 新聞標題2 | 2020-06-18 14:15 |     https://news.ltn.com.tw/news/Yunlin/paper/1383368    | example content |  自由  |  生活 |   name2  |



