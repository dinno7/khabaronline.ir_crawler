First create a virtual environment and install below libs:

Creating environment(py version 3.10)
```bash
python3.10 -m venv venv
```

Installing packages
```bash
pip install scrapy jdatetime pymongo hazm flask scikit-learn
```

### RUN mongodb on port 27017 or set it URI in `/news_scraper/news_scraper/settings.py`

Then go to `news_scraper` directory and run below command to crawling the khabaronline.ir:
```bash
scrapy crawl news-spider
```
Then you can run the web application to search in results:

```bash
python web-app/index.py
```

