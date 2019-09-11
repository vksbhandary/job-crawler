# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os, shutil
import json
import random
import hashlib
#https://stackoverflow.com/questions/30970436/scrapy-reactornotrestartable-one-class-to-run-two-or-more-spiders
#from twisted.internet import reactor

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

monster_cat="juju_cat.json"
monster_cat_format="json"
directory="cache/"
proc_dir="proc/"
proc_file_ext=".proc"

current_PID=os.getpid()
if not os.path.exists(proc_dir):
    os.makedirs(proc_dir)

if not os.path.isfile(proc_dir+str(current_PID)+proc_file_ext):
    pidfile=open(proc_dir+str(current_PID)+proc_file_ext,'a')
    pidfile.close()

########
#   checking if categries already accessed
#########
filename="cache/"+monster_cat
if not os.path.exists(directory):
    os.makedirs(directory)
# ok now executing crawler if the categories are not crawled before
if not os.path.isfile(filename):
    settings=get_project_settings()
    settings.overrides['FEED_FORMAT'] = monster_cat_format
    settings.overrides['FEED_URI'] = filename
    process = CrawlerProcess(settings)
    process.crawl('generalcat')
    process.start() # the script will block here until the crawling is finished
    reactor.run()

#process.crawl(SomeSpider, start_urls=["http://www.example.com"])
## read the json
with open(filename) as data_file:
    catdata = json.load(data_file)
    category=random.choice(catdata)
    rand_link=random.choice(category['links'])
    jobdir="cache/jobs/"
    #if os.path.exists(jobdir):
    #    shutil.rmtree(jobdir)
    #os.makedirs(jobdir)
    #now starting cralwer to crawl random category
    settings=get_project_settings()
    name=jobdir+hashlib.md5(rand_link['url']).hexdigest()+".json"
    settings.overrides['FEED_FORMAT'] = monster_cat_format
    settings.overrides['FEED_URI'] = name
    process = CrawlerProcess(settings)
    process.crawl('generalcrawl', start_urls=[rand_link['url']])
    process.start() # the script will block here until the crawling is finished

try:
    os.remove(proc_dir+str(current_PID)+proc_file_ext)
except OSError:
    pass
