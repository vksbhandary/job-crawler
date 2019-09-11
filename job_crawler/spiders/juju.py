# -*- coding: utf-8 -*-
import scrapy
import re
from job_crawler.items import JobCrawlerItem
from job_crawler import JobCrawlerSettings
from urlparse import urlparse

class JujuSpider(scrapy.Spider):
    name = "juju"
    allowed_domains = JobCrawlerSettings.allowed_domains
    start_urls = (
        'http://www.juju.com/category/accounting/',
    )

    def parse(self, response):
        #jobs = []
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        for sections in response.css('div.article div ul.job_results li dl.job'):
            job = JobCrawlerItem()
            job['title']=sections.css('dt p a::text').extract_first()
            link=sections.css('dt p a::attr(href)').extract_first()
            job['link']=link
            job['site']='juju'
            companynLoc=sections.css('dd.company::text').extract_first()
            job['company']=companynLoc.split(" (",1)[0]
            job['location']=companynLoc.split(" (")[-1].split(")")[0]
            sourcenDate=sections.css('dd.options div.source::text').extract_first()
            time=sourcenDate.split("(")[-1].split(")")[0]
            job['time']=time
            yield job
            #dig a little deeper
            #if sections.css('div.jobTitle h2 a::attr(href)').extract_first():
            #    request = scrapy.Request(link,callback=self.parse_Job_Main_page)
            #    request.meta['job'] = job
        nextlink=response.css("ul.pagelinks li a[title='Next Page']::attr(href)").extract_first()
        if nextlink is not None:
            yield scrapy.Request(domain+nextlink, callback=self.parse)

            #jobs.append(job)
