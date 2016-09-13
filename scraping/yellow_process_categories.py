# -*- coding: utf-8 -*-

import os.path
import re
import scrapy
from scrapy.spiders import Spider
from time import sleep

list_path = "/home/navendu/Downloads/categories.txt"
file_path = "/home/navendu/Downloads/already_visited.txt"
url = "http://www.yellowpages.in/"
page_start = 1
num_pages = 1

class MySpider(Spider):

    name = "yellow_spider"
    start_urls = [url]

    # make list of already visited end urls in a file!
    def already_visited_file(self, link_visited):
        f = open(file_path, 'a')
        f.write(link_visited)
        f.write("\n")
        f.close()


    # get data from end result page!
    def parse_end_result(self, response):
        dct = {'address': None,
               'phone': None,
               'website': None,
               'listing_url': response.url}

        for item in response.xpath('//div[@class="addressblock"]/div/span/div/text()').extract():
            if item.strip():
                dct['address'] = ' '.join(item.split())
        for item in response.xpath('//div[@class="addressblock"]/div/ul/li/text()').extract():
            lines = item.split('\n')
            for line in lines:
                if 'Call : ' in line:
                    dct['phone'] = line.strip()

        for item in response.xpath('//div[@class="addressblock"]/div/ul/li/a/text()').extract():
            if item.strip():
                dct['website'] = item.strip()

        if dct['address'] or dct['phone'] or dct['website']:
            print dct
            print "\n"


    # iterate over one category page!
    # make list of results!
    def parse_category(self, response):
        end_results = []
        for item in response.xpath('//a').extract():
            m = re.search("http://www.yellowpages.in/listing/.*html", item)
            if m:
                if m.group() not in end_results:
                    end_results.append(m.group())


        for end_result in end_results:
            # CHECK IF LINK NOT IN ALREADY VISITED FILE!
            if os.path.exists(file_path):
                f = open(file_path, 'r')
                if end_result in f.read():
                    continue
                f.close()
            
            self.already_visited_file(end_result)
            yield scrapy.Request(end_result, callback=self.parse_end_result)


    def parse(self, response):

        global page_start
        global num_pages
        
        while num_pages != 0:

            # read first category from file and process
            if os.path.exists(list_path):
                f = open(list_path, 'r')
                first_line = f.readline()
                first_line_items = first_line.split('^^^^')
                category = first_line_items[1].strip()

                # UPDATE FILE WITH PAGE/SCREEN PROCESSED
                os.remove(list_path)
                lines = [line for line in f.readlines()]
                f = open(list_path, 'w')
                first_line_updated = first_line_items[0] + " ^^^^ " + first_line_items[1] + " ^^^^ " + str(page_start)
                f.write(first_line_updated)
                f.write("\n")
                for line in lines[1:]:
                    f.write(line)
                f.close()

                yield scrapy.Request(category + '&screen=%s' % page_start, callback=self.parse_category)
                # wait for 1 sec
                sleep(1)
            else:
                raise Exception("CATEGORIES NOT FOUND")

            num_pages -= 1
            page_start += 1

