# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from datetime import datetime
from scrapy.exceptions import DropItem


class MongoPipelineModpack(object):
    date_format = "%d.%m.%Y, %H:%M:%S"
    client = None


    def open_spider(self, spider):
        self.client = pymongo.MongoClient(spider.parsed_args['address'],
                                          username=spider.parsed_args['username'],
                                          password=spider.parsed_args['password'],
                                          authSource=spider.parsed_args['authSource'],
                                          authMechanism=spider.parsed_args['authMechanism'])

        self.mongo_db = self.client["twitchCrawl"]
        self.col = self.mongo_db["Modpack"]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        db_entry = self.col.find_one({"name": item["name"]})
        if db_entry is not None:
            lastupdated_old = datetime.strptime(db_entry["lastUpdated"], "%d.%m.%Y, %H:%M:%S")
            lastupdated_new = datetime.strptime(item["lastUpdated"], "%d.%m.%Y, %H:%M:%S")
            if lastupdated_new == lastupdated_old:
                raise DropItem()
            else:
                self.col.find_one_and_update({"name": item["name"]}, {"$set": dict(item)}, upsert=True)
                return item
        else:
            self.col.find_one_and_update({"name": item["name"]}, {"$set": dict(item)}, upsert=True)
            return item




class MongoPipelineBuilds(object):
    date_format = "%d.%m.%Y, %H:%M:%S"

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(spider.parsed_args['address'],
                                          username=spider.parsed_args['username'],
                                          password=spider.parsed_args['password'],
                                          authSource=spider.parsed_args['authSource'],
                                          authMechanism=spider.parsed_args['authMechanism'])
        self.mongo_db = self.client["twitchCrawl"]
        self.col = self.mongo_db["ModpackBuilds"]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        print("Process Item")
        print(item)
        self.col.find_one_and_update({"name": item["name"], "version": item["version"]}, {"$set": dict(item)}, upsert=True, new=True)

