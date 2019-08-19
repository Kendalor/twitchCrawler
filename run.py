from twitchCrawler.spiders.twitch_spider import TwitchSpider
from scrapy.crawler import CrawlerProcess
from twitchCrawler.spiders.modpack_build_spider import BuildSpider
import pymongo
import datetime
import json
import time
from multiprocessing import Process
import argparse
import sys



def string2date(string1):
    return datetime.datetime.strptime(string1, "%d.%m.%Y, %H:%M:%S")

def filter_todos(entry):
    print(entry,type(entry))
    if entry["lastScanned"] is '':
        return True
    else:
        if string2date(entry["lastUpdated"]) > string2date(entry["lastScanned"]):
            return True
        else:
            return False


def twitchcrawler(parsed_args):
    crawlTwitch(TwitchSpider,
          json.dumps(vars(parsed_args)),
          {
        "ITEM_PIPELINES": {'twitchCrawler.pipelines.MongoPipelineModpack': 300},
        "BOT_NAME": 'twitchCrawler',
        "ROBOTSTXT_OBEY": True
    })


def crawlTwitch(spider, args, settings):
    crawler = CrawlerProcess(settings=settings)
    crawler.crawl(spider, parsed_args=args)
    crawler.start()

def crawlMods(spider, args, settings, start_urls):
    crawler = CrawlerProcess(settings=settings)
    crawler.crawl(spider, parsed_args=args, start_urls=start_urls)
    crawler.start()

def buildCrawler(parsed_args):

    client = pymongo.MongoClient(parsed_args.address,
                                      username=parsed_args.username,
                                      password=parsed_args.password,
                                      authSource=parsed_args.authSource,
                                      authMechanism=parsed_args.authMechanism)
    mongo_db = client["twitchCrawl"]
    col = mongo_db["Modpack"]

    watchlist = col.find({"onWatchlist": True}, {"name": 1, "siteLink": 1, "lastUpdated": 1, "lastScanned": 1})
    #for entry in watchlist:
     #   print(entry, type(entry))
    todos = [entry for entry in watchlist if filter_todos(entry)]
    for job in todos:
        url = job["siteLink"]+'/files/all'
        time.sleep(3)
        try:
            p = Process(target=crawlMods, args=(BuildSpider, json.dumps(vars(parsed_args)), {
                "ITEM_PIPELINES": {'twitchCrawler.pipelines.MongoPipelineBuilds': 300},
                "BOT_NAME": 'twitchCrawler',
                "ROBOTSTXT_OBEY": True}, json.dumps([url])))
            p.start()
            p.join()
            if p.exitcode is 0:
                col.update_one({"name": job["name"]}, {"$set": {"lastScanned": datetime.datetime.now().strftime("%d.%m.%Y, %H:%M:%S")}}, upsert=True)
        except Exception as e:
            print("Failed to Crawl: " + url)


class TwitchCrawler:

    def __init__(self, args):
        parser = argparse.ArgumentParser(description='TwitchCrawler')
        parser.add_argument('-address',
                            action="store",
                            type=str, dest="address",
                            required=True,
                            help="Address of MongoDB")
        parser.add_argument('-user',
                            action="store",
                            type=str, dest="username",
                            required=True,
                            help="Username of MongoDB")
        parser.add_argument('-pw',
                            action="store",
                            type=str,
                            dest="password",
                            required=True,
                            help="Password of MongoDB")
        parser.add_argument('-authSource',
                            action="store",
                            type=str,
                            dest="authSource",
                            required=True,
                            help="AuthSource of MongoDB")
        parser.add_argument('-authMechanism',
                            action="store",
                            type=str,
                            dest="authMechanism",
                            required=True,
                            help="authMechanism of MongoDB")
        parser.add_argument('-wait',
                            action="store",
                            type=int,
                            dest="wait",
                            required=False,
                            default=21600,
                            help="Wait in Seconds between Complete Crawls")
        self.parsed_args = parser.parse_args(args)
        print(self.parsed_args)
        self.mongodb_client = pymongo.MongoClient(self.parsed_args.address,
                                          username=self.parsed_args.username,
                                          password=self.parsed_args.password,
                                          authSource=self.parsed_args.authSource,
                                          authMechanism=self.parsed_args.authMechanism)


    def run(self):
        while True:
            args = self.parsed_args
            #p1 = Process(target=twitchcrawler, args=(args,))
            p2 = Process(target=buildCrawler, args=(args,))
            #p1.start()
            p2.start()
            #p1.join()
            p2.join()
            print("Waiting "+str(self.parsed_args.wait)+" Seconds")
            time.sleep(self.parsed_args.wait)


if __name__ == '__main__':
    try:
        cwlr = TwitchCrawler(sys.argv[1:])
    except:
        exit()
    cwlr.run()