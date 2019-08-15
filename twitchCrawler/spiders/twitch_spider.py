import scrapy
from scrapy.loader import ItemLoader
from twitchCrawler.items import Modpack
from datetime import datetime
import json

class TwitchSpider(scrapy.Spider):

    def __init__(self, parsed_args, *args, **kwargs):
        super(TwitchSpider, self).__init__(*args, **kwargs)
        self.parsed_args = json.loads(parsed_args)
        print("After TwitchSpiderInit")
        print(self.parsed_args)
    name = "twitch"
    start_urls = [
        'https://www.curseforge.com/minecraft/modpacks'
    ]

    def parse(self, response):

        for modpack in response.xpath('/html/body/div[1]/main/div[1]/div[2]/section/div[2]/div/div[3]/div/div/div'):
            l = ItemLoader(item=Modpack(), selector=modpack)
            l.add_value('name', modpack.xpath('.//h3/text()').get())
            l.add_value('author', modpack.xpath('.//a[2]/text()').get())
            l.add_value('lastUpdated', datetime.strptime(modpack.xpath('.//span[2]/abbr/text()').get(), "%b %d, %Y"
                                                         ).strftime("%d.%m.%Y, %H:%M:%S"))
            l.add_value('siteLink', response.urljoin(modpack.xpath('.//a[1]').attrib['href']))
            yield l.load_item()
        if(len(response.xpath(
                '/html/body/div[1]/main/div[1]/div[2]/section/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/a')) > 0):
            next_page = response.xpath(
                '/html/body/div[1]/main/div[1]/div[2]/section/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/a'
            ).attrib['href']
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)
