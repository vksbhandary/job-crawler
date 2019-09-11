# -*- coding: utf-8 -*-
import scrapy
from urlparse import urlparse

class JujucatSpider(scrapy.Spider):
    name = "jujucat"
    allowed_domains = ["www.juju.com"]
    start_urls = (
        'http://www.juju.com/category/',
    )


def parse(self, response):
            #for sections in response.css('div.section.top-jobs-section div.row div.caption'):
            parsed_uri = urlparse(response.url)
            domain = '{uri.netloc}'.format(uri=parsed_uri)
            section = JobCategoryItem()
            section['catname']="Jobs by category"
            section['links']=[]
            for links in response.css('article.content div.cols_block_3 div ul li'):
                link={}
                link['text']=links.css('a::text').extract_first()
                link['url']=domain+links.css('a::attr(href)').extract_first()
                section['links'].append(link)
            yield section
