import scrapy
from twitchCrawler.items import ModpackBuild, ModpackBuildItemLoader
import json
import pymongo

class BuildSpider(scrapy.Spider):

    name = "BuildSpider"
    start_urls=[]
    def __init__(self, start_urls, parsed_args, *args, **kwargs):
        super(BuildSpider, self).__init__(*args, **kwargs)
        self.start_urls = json.loads(start_urls)
        self.parsed_args = json.loads(parsed_args)


    def parse(self, response):
        for row in response.xpath(
                '/html/body/div[1]/main/div[1]/div[2]/section/div/div/div/section/div[2]/div/table/tbody/tr'):
            next_page = row.xpath(".//td[2]/a[1]/@href").get()
            print(next_page)
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse_build)

    def parse_build(self, response):
        loader = ModpackBuildItemLoader(item=ModpackBuild(), respone=response)
        loader.add_value('release', response.xpath('/html/body/div[1]/main/div[1]/div[2]/section/div/div/div/section/section[1]/article/div[1]/div[1]/div/div/span/text()').get())
        if response.xpath("/html/body/div[1]/main/div[1]/div[2]/section/div/div/div/section/section[1]/article/div[1]/div[2]/div[1]/a/@href").get() is not None:
            loader.add_value('clientFileLink', response.urljoin(response.xpath("/html/body/div[1]/main/div[1]/div[2]/section/div/div/div/section/section[1]/article/div[1]/div[2]/div[1]/a/@href").get()))
        if response.xpath('//*[@id="additional-files"]/div/div/div/table/tbody/tr/td[7]/div/a/@href').get() is not None:
            loader.add_value('serverFileLink', response.urljoin(response.xpath('//*[@id="additional-files"]/div/div/div/table/tbody/tr/td[7]/div/a/@href').get()))
        loader.add_value('name', response.xpath(
                   '/html/body/div[1]/main/div[1]/header/div[3]/div[1]/div/div[1]/h2/text()').get())
        loader.add_value('version', response.xpath("/html/body/div[1]/main/div[1]/div[2]/section/div/div/div/section/section[1]/article/div[1]/div[1]/a/h3/text()").get())
        yield loader.load_item()
