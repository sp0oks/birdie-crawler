# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import bson

from scrapy.exceptions import DropItem

class MongoDBPipeline(object):
    collection = 'items'

    def __init__(self, mongo_uri, db_name):
        self.mongo_uri = mongo_uri
        self.db_name = db_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(mongo_uri=crawler.settings.get('MONGODB_URI'),
                   db_name=crawler.settings.get('MONGODB_DATABASE'))

    def open_spider(self, spider):
        self.connection = pymongo.MongoClient(self.mongo_uri)
        self.db = self.connection[self.db_name]

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        if 'preco' not in item or 'titulo' not in item:
            raise DropItem('Invalid item (required fields missing!): %s' % item)
        self.db[self.collection].find_one_and_replace(
                {'url': item['url']},
                {
                    'dominio': item['dominio'],
                    'url': item['url'],
                    'categoria': item['categoria'],
                    'titulo': item['titulo'],
                    'disponivel': item.get('disponivel', None),
                    'moeda': item.get('moeda', 'R$'),
                    'preco': bson.Decimal128(item['preco']),
                    'descricao': item['descricao'],
                    'caracteristicas': item['caracteristicas']
                }, upsert=True)
        return item

