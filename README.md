# news_crawler

This tool is used for extracting daily news (Traditional Chinese) from different sources in Taiwan, include:
- [x] LTN (Done)
- [x] Yunlin County Government (Done)
- [ ] ChinaTimes (TBD)
- [ ] UDN (TBD)
- [ ] EBC (TBD)

## Installation
### with conda 
```bash
git clone https://github.com/MingLunWu/news_crawler.git
cd news_crawler
conda env create -f environment.yml
```

## Usage 
### Set config.json
```json
{
    "keyword":["雲林","雲縣"],  
    "start_date": "None", 
    "end_date": "None" 
}
```
+ **keyword** : To filter the news that contains at least one keyword in the title or content field.
+ **start_date** : Define the time interval for the tool to retrieve news. (format: `yyyy-mm-dd`, 2020-06-20, "none" and "today" means today.)
+ **end_date**: Define the time interval for the tool to retrieve news. (format: `yyyy-mm-dd`, 2020-06-20, "none" and "today" means today.)

### Run the script.
Make sure the virtual environment have already been created through conda command and `config.json` has been set.

```bash
bash start.sh
```
