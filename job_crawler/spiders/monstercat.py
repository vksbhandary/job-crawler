# -*- coding: utf-8 -*-
import scrapy
from job_crawler.items import JobCategoryItem


class MonstercatSpider(scrapy.Spider):
    name = "monstercat"
    allowed_domains = ["monster.com"]
    start_urls = (
        'https://www.monster.com/jobs/',
    )

    def parse(self, response):

        for sections in response.css('div.section.top-jobs-section div.row div.caption'):
            section = JobCategoryItem()
            section['catname']=sections.css('h3::text').extract_first()
            section['links']=[]
            for links in sections.css('ul.card-columns li'):
                link={}
                link['text']=links.css('a::text').extract_first()
                link['url']=links.css('a::attr(href)').extract_first()
                section['links'].append(link)

            yield section
