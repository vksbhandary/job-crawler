# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os, shutil
import json
#import random
import hashlib
import sys

from job_crawler import JobCrawlerSettings

def get_last_id(link):
    if os.path.isfile(JobCrawlerSettings.statsFile):
        with open(JobCrawlerSettings.statsFile) as data_file:
            statsdata = json.load(data_file)
            hash=hashlib.md5(link).hexdigest()
            if statsdata[hash]["last_id"] is not None or statsdata[hash]["last_id"] is not "":
                return statsdata[hash]["last_id"]
    return None

def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    site=sys.argv[1]
    link=sys.argv[2]
    settings=get_project_settings()
    jobdir=JobCrawlerSettings.joboutputdir
    name=jobdir+hashlib.md5(link).hexdigest()+"."+JobCrawlerSettings.catoutputfiles[site]['format']
    settings.overrides['FEED_FORMAT'] = JobCrawlerSettings.catoutputfiles[site]['format']
    settings.overrides['FEED_URI'] = name
    process = CrawlerProcess(settings)
    last_id=get_last_id(link)
    if last_id is not None and link is not None:
        process.crawl('generalcrawl', start_urls=[link], lastupdate=last_id)
    elif link is not None:
        process.crawl('generalcrawl', start_urls=[link])
    else:
        process.crawl('generalcrawl')
    process.start() # the script will block here until the crawling is finished


if __name__ == "__main__":
    main()
