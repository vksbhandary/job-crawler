# -*- coding: utf-8 -*-
import scrapy
import re
from job_crawler.items import JobCrawlerItem
from job_crawler import JobCrawlerSettings
from urlparse import urlparse
import hashlib
import datetime
#import logging

#from datetime import date

class GeneralcrawlSpider(scrapy.Spider):
    name = "generalcrawl"
    allowed_domains = JobCrawlerSettings.allowed_domains
    start_urls = (
                'http://www.juju.com/category/accounting/',
                )

    def __init__(self,start_urls, lastupdate = None, maxdaydiff= 60, maxdepth=4):
        self.lastupdate = lastupdate
        self.maxdepth = maxdepth
        self.maxdaydiff = maxdaydiff
        self.start_urls=start_urls

    def parse(self, response):
            #jobs = []
            parsed_uri = urlparse(response.url)
            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            category=JobCrawlerSettings.crawlerCatLinks[domain]['category']
            matadata=JobCrawlerSettings.crawlerMainDB[category]
            needtogoindepth=True;
            today = datetime.datetime.now()
            #util=JobCrawlerSettings()

            if matadata is not None:
                for key in matadata:
                    sectionsCSS=matadata[key]['item']['containercss']
                    for sections in response.css(sectionsCSS):
                        job = JobCrawlerItem()
                        jobtitle=sections.css(matadata[key]['item']['jobtitle']['css']).extract_first()
                        joblink=sections.css(matadata[key]['item']['joblink']['css']).extract_first()
                        jobsite=matadata[key]['item']['jobsite']
                        jobcompany=sections.css(matadata[key]['item']['jobcompany']['css']).extract_first()
                        joblocation=sections.css(matadata[key]['item']['joblocation']['css']).extract_first()
                        jobtime=sections.css(matadata[key]['item']['jobtime']['css']).extract_first()

                        #title
                        title_typ=matadata[key]['item']['jobtitle']['type']
                        title=JobCrawlerSettings.return_ext_attr(jobtitle,title_typ)
                        job['title']=title

                        #job link
                        if matadata[key]['item']['domainappend']==1:
                            job['link']=domain+joblink
                        else:
                            job['link']=joblink

                        job['site']=jobsite

                        #company
                        comp_typ=matadata[key]['item']['jobcompany']['type']
                        company=JobCrawlerSettings.return_ext_attr(jobcompany,comp_typ)
                        job['company']=company

                        #location
                        loc_typ=matadata[key]['item']['joblocation']['type']
                        location=JobCrawlerSettings.return_ext_attr(joblocation,loc_typ)
                        job['location']=location

                        #time
                        time_typ=matadata[key]['item']['jobtime']['type']
                        time=JobCrawlerSettings.return_ext_attr(jobtime,time_typ)
                        jobdate=datetime.datetime.strptime(time, matadata[key]['timeformat'])
                        formated_time=jobdate.strftime(JobCrawlerSettings.standardTimeFormat)
                        job['time']=formated_time
                        yield job

                        #calculate hash to track
                        #stringhsh=jobtitle+jobcompany+joblocation+jobtime
                        record={"time":formated_time,"company":company,"title":title}
                        hashStr=JobCrawlerSettings.return_job_record_id(record)
                        #hashStr=hashlib.md5(stringhsh.encode('utf-8')).hexdigest()
                        if hashStr==self.lastupdate:
                            needtogoindepth=False
                            #print ("Synced Finished (Reached to a point where we stopped previously)")
                            self.logger.info("Synced Finished (Reached to a point where we stopped previously)")
                        #checking if the date difference is more than we want
                        delta = today - jobdate
                        if delta.days > self.maxdaydiff:
                            needtogoindepth=False
                            #print ("Starting to encounter old jobs (%d days old)" % (self.maxdaydiff))
                            self.logger.info("Starting to encounter old jobs (%d days old)" , self.maxdaydiff)

                        #dig a little deeper
                        #if sections.css('div.jobTitle h2 a::attr(href)').extract_first():
                        #    request = scrapy.Request(link,callback=self.parse_Job_Main_page)
                        #    request.meta['job'] = job
                    nxtlink=response.css(matadata[key]['nextpage']).extract_first()
                    # incrementing depth
                    if "present_depth" not in response.meta:
                        response.meta["present_depth"]=0;

                    response.meta["present_depth"]=response.meta["present_depth"]+1

                    if response.meta["present_depth"]-1 > self.maxdepth:
                        needtogoindepth=False
                        self.logger.info("Reached maximum depth of %d pages.", self.maxdepth)
                        #print ("Reached maximum depth of %d pages."% (self.maxdepth))

                    if nxtlink is not None:
                        if matadata[key]['nextdomainappend']==1:
                            nxtlink=domain+nxtlink

                        #check if we need to go more deep
                        if needtogoindepth:
                            yield scrapy.Request(nxtlink, callback=self.parse, meta={'present_depth': response.meta["present_depth"]})

                #jobs.append(job)
