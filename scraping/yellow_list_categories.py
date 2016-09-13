# -*- coding: utf-8 -*-

import os.path
import re
import scrapy
from scrapy.spiders import Spider
from time import sleep

url = "http://www.yellowpages.in/"
list_path = "/home/navendu/Downloads/categories.txt"


class MySpider(Spider):

    name = "list_spider"
    start_urls = [url]

    def parse(self, response):

        for item in response.xpath('//a').extract():
            item = item.strip()

            # get valid categories!
            if 'listing/results.php?categories=' in item:
                name = None
                link = None

                items = item.split("</a>", 1)
                if len(items) == 2:
                    subitems = items[0].split('>')
                    name = subitems[len(subitems)-1].strip()

                items = item.split("<a href=\"", 1)
                if len(items) == 2:
                    subitems = items[1].split("\"")
                    link = subitems[0].strip()

                if name and link:
                    f = open(list_path, 'a')
                    f.write("%s ^^^^ %s ^^^^ %s" % (name, link, 0))
                    f.write("\n")
                    f.close()


