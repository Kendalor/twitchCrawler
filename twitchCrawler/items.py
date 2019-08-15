# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst, MapCompose
import re


def grepVersion(inString):
    m = re.search("[0-9]+\.[0-9]+\.[0-9]+", inString)
    return m.group()


class Modpack(scrapy.Item):

    name = scrapy.Field(output_processor=TakeFirst())
    author = scrapy.Field(output_processor=TakeFirst())
    lastUpdated = scrapy.Field(output_processor=TakeFirst())
    siteLink = scrapy.Field(output_processor=TakeFirst())


class ModpackBuild(scrapy.Item):
    name = scrapy.Field()
    release = scrapy.Field()
    version = scrapy.Field()
    clientFileLink = scrapy.Field()
    serverFileLink = scrapy.Field()


class ModpackBuildItemLoader(scrapy.loader.ItemLoader):
    default_output_processor = TakeFirst()
    version_in = MapCompose(grepVersion)