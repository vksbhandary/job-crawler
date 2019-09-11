# -*- coding: utf-8 -*-
import scrapy
from urlparse import urlparse

from job_crawler import JobCrawlerSettings
from job_crawler.items import JobCategoryItem

class GeneralcatSpider(scrapy.Spider):
    name = "generalcat"
    allowed_domains = JobCrawlerSettings.allowed_domains
    start_urls = (
        'https://www.monster.com/jobs/',
    )
    def __init__(self,start_urls):
        self.start_urls=start_urls

    def parse(self, response):
                #for sections in response.css('div.section.top-jobs-section div.row div.caption'):
                parsed_uri = urlparse(response.url)
                domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
                catdata=JobCrawlerSettings.crawlerCatDB[response.url]
                if catdata is not None and "superloop" not in catdata:
                    for key in catdata:
                        section = JobCategoryItem()
                        section['catname']=catdata[key]['catname']
                        section['links']=[]
                        container=catdata[key]['looper']['containercss']
                        for links in response.css(container):
                                link={}
                                text=catdata[key]['looper']['cattext']
                                url=catdata[key]['looper']['caturl']
                                link['text']=links.css(text).extract_first()
                                href=links.css(url).extract_first()
                                if catdata[key]['looper']['domainappend']==1:
                                    link['url']=domain+href
                                else:
                                    link['url']=href

                                section['links'].append(link)
                        yield section
                elif catdata is not None and "superloop" in catdata:
                    for sections in response.css(catdata["superloop"]):
                        section = JobCategoryItem()
                        section['catname']=sections.css(catdata['catname']).extract_first()
                        section['links']=[]
                        container=catdata['looper']['containercss']
                        for links in sections.css(container):
                                link={}
                                text=catdata['looper']['cattext']
                                url=catdata['looper']['caturl']
                                link['text']=links.css(text).extract_first()
                                href=links.css(url).extract_first()
                                if catdata['looper']['domainappend']==1:
                                    link['url']=domain+href
                                else:
                                    link['url']=href

                                section['links'].append(link)
                        yield section
