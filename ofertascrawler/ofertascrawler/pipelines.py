# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo


class MongoDBPipeline(object):
    collection = 'items'

    def __init__(self, mongo_uri, db_name):
        self.mongo_uri = mongo_uri
        self.db_name = db_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(mongo_uri=crawler.settings.get('MONGO_URI'),
                   db_name=crawler.settings.get('MONGO_DATABASE'))

    def open_spider(self, spider):
        self.connection = pymongo.MongoClient(self.mongo_uri)
        self.db = self.connection[self.db_name]

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        self.db[self.collection].insert_one(dict(item))
        return item
 
