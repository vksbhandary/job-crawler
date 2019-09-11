# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os, shutil
import json
import random
import hashlib
import sys
import subprocess

from job_crawler import JobCrawlerSettings

def init():
    current_PID=os.getpid()
    proc_dir=JobCrawlerSettings.processDir
    proc_file_ext=JobCrawlerSettings.processFileExt
    if not os.path.exists(proc_dir):
        os.makedirs(proc_dir)
    if not os.path.isfile(proc_dir+str(current_PID)+proc_file_ext):
        pidfile=open(proc_dir+str(current_PID)+proc_file_ext,'a')
        pidfile.close()
    return current_PID

def get_cat_links_list(filename):
    with open(filename) as data_file:
        catdata = json.load(data_file)
        return catdata

def crawl_site_category_link(site):
    with open(JobCrawlerSettings.site_cat_file) as data:
        catdata = json.load(data)
        url=catdata[site]["links"]
        settings=get_project_settings()
        settings.overrides['FEED_FORMAT'] = JobCrawlerSettings.catoutputfiles[site]['format']
        settings.overrides['FEED_URI'] = JobCrawlerSettings.catoutputfiles[site]['file']
        process = CrawlerProcess(settings)
        process.crawl('generalcat', start_urls=url)
        process.start() # the script will block here until the crawling is finished
        #reactor.run()

def remove_pid(current_PID):
    try:
        os.remove(JobCrawlerSettings.processDir+str(current_PID)+JobCrawlerSettings.processFileExt)
    except OSError:
        pass

def crawl_link(site,link):
    settings=get_project_settings()
    jobdir=JobCrawlerSettings.joboutputdir
    name=jobdir+hashlib.md5(link).hexdigest()+"."+JobCrawlerSettings.catoutputfiles[site]['format']
    settings.overrides['FEED_FORMAT'] = JobCrawlerSettings.catoutputfiles[site]['format']
    settings.overrides['FEED_URI'] = name
    process = CrawlerProcess(settings)
    last_id=get_last_id(link)
    if last_id is not None:
        process.crawl('generalcrawl', start_urls=[link], lastupdate=last_id)
    else:
        process.crawl('generalcrawl', start_urls=[link])
    process.start() # the script will block here until the crawling is finished

def get_last_id(link):
    if os.path.isfile(JobCrawlerSettings.statsFile):
        with open(JobCrawlerSettings.statsFile) as data_file:
            statsdata = json.load(data_file)
            hash=hashlib.md5(link).hexdigest()
            if statsdata[hash][last_id] is not None:
                return statsdata[hash][last_id]
    return None


def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    current_PID=init()
    site=sys.argv[1]
    if site is None:
         site='juju'
    filename=JobCrawlerSettings.outputdir+JobCrawlerSettings.catoutputfiles[site]['file']
    if not os.path.isfile(filename):
        crawl_site_category_link(site)
    with open(filename) as data_file:
        catlinksdata = json.load(data_file)
        with open(JobCrawlerSettings.site_cat_file) as data:
            catsettingdata = json.load(data)
            categories=catsettingdata[site]["catnames"]
            for catlinkrec in catlinksdata:
                print("category:"+catlinkrec["catname"])
                if catlinkrec["catname"] in categories:
                    for catkey in catlinkrec["links"]:
                        print("Scraping link:"+catkey['url'])
                        link=catkey['url']
                        subprocess.call(["python", "runner.py",site,link])
                        #crawl_link(site,link)


if __name__ == "__main__":
    main()
