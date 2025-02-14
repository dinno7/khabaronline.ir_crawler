# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
import sys

current_file_path = os.path.abspath(__file__)
parent_directory = os.path.dirname(current_file_path)
root_directory = os.path.dirname(os.path.dirname(parent_directory))
sys.path.append(root_directory)


import logging
from datetime import datetime

import pymongo

from utils import preprocess_text_fa


class PreprocessingPipeline:
    def convert_fa_numbers_to_en(self, text):
        fa_to_en_map = {
            "۰": "0",
            "۱": "1",
            "۲": "2",
            "۳": "3",
            "۴": "4",
            "۵": "5",
            "۶": "6",
            "۷": "7",
            "۸": "8",
            "۹": "9",
        }

        for fa_num, en_num in fa_to_en_map.items():
            text = text.replace(fa_num, en_num)

        return text

    def process_item(self, item, spider):
        # > Convert all Persian number letters to English version
        for key in item:
            if type(item[key]) == str:
                item[key] = self.convert_fa_numbers_to_en(item[key])

        must_normalize_keys = ["processed_content_text", "processed_title"]
        for key in must_normalize_keys:
            if key in item:
                item[key] = preprocess_text_fa(item[key])

        return item


class MongoDBPipeline(object):
    collection_name = "news"

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        ## pull in information from settings.py
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE"),
        )

    def open_spider(self, spider):
        ## initializing spider
        ## opening db connection
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        ## clean up when spider is closed
        self.client.close()

    def process_item(self, item, spider):
        ## how to handle each post
        logging.debug("💀 > ADDING...")

        self.db[self.collection_name].update_one(
            {"news_code": item["news_code"]},
            {
                "$set": {**dict(item), "updatedAt": datetime.now()},
                "$setOnInsert": {"createdAt": datetime.now()},
            },
            upsert=True,
        )

        logging.debug("💀 > News added to MongoDB")
        return item
