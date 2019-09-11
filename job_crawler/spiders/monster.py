# -*- coding: utf-8 -*-
import scrapy
import re
import json
from job_crawler.items import JobCrawlerItem
from urlparse import urlparse
from job_crawler import JobCrawlerSettings

#from scrapy.utils.project import get_project_settings

#https://stackoverflow.com/questions/33503643/get-data-from-script-tag-in-html-using-scrapy
#https://stackoverflow.com/questions/8467700/how-do-i-merge-results-from-target-page-to-current-page-in-scrapy

class MonsterSpider(scrapy.Spider):
    name = "monster"
    allowed_domains = JobCrawlerSettings.allowed_domains
    start_urls = (
        'https://www.monster.com/jobs/q-graphic-design-jobs.aspx',
    )

    def parse(self, response):
        #jobs = []
        for sections in response.css('#resultsWrapper div.js_result_container'):
            job = JobCrawlerItem()
            job['title']=sections.css('div.jobTitle h2 a span::text').extract_first()
            link=sections.css('div.jobTitle h2 a::attr(href)').extract_first()
            job['link']=link
            job['site']='monster'
            job['company']=sections.css('div.company a span::text').extract_first()
            job['location']=sections.css('div.row div.job-specs-location p a::text').extract_first()
            job['time']=sections.css('div.job-specs-date p time::attr(datetime)').extract_first()
            #dig a little deeper
            #if sections.css('div.jobTitle h2 a::attr(href)').extract_first():
            #    request = scrapy.Request(link,callback=self.parse_Job_Main_page)
            #    request.meta['job'] = job
            yield job
            #jobs.append(job)


#        return(jobs)



# Not generic enought because link redirects to random site
# So not using this method right now
    def parse_Job_Main_page(self, response):
        self.logger.info("Visited %s", response.url)
        job = response.meta['job']
        parsed_uri = urlparse(response.url)
        domain = '{uri.netloc}'.format(uri=parsed_uri)

        if domain=='www.techcareers.com':
            job['details']=response.css("div.featured-job-description::text").extract_first()

        if domain=='job-openings.monster.com':
            data=response.css("div#JobViewContent script[type='application/ld+json']::text").extract_first()
            parsedJSON= json.loads(data)
            job['details']=parsedJSON['description']
            job['jobtype']=parsedJSON['employmentType']

        return job
