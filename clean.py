# -*- coding: utf-8 -*-
import os, shutil
import json
import random
import hashlib
from glob import glob
from job_crawler import JobCrawlerSettings
from database import add_job_record
from report import send_email
import time
MAX_WAIT_TIME=2

def read_update_job_db():
    for file_name in glob(JobCrawlerSettings.joboutputdir+'*.json'):
        category_hash=file_name.split("/")[-1].split(".")[0]
        print category_hash
        print file_name
        with open(file_name) as data_file:
            jobdata = json.load(data_file)
            total_records=0
            last_job_id=""
            directory=""
            for jobrecord in jobdata:
                #print jobrecord
                # We need to prepare the records for adding to database
                #sprint jobrecord['location'].strip()
                if "summary" not in jobrecord:
                    jobrecord['summary']="null"
                elif jobrecord["summary"] is None or jobrecord["summary"]=="":
                    jobrecord['summary']="null"

                #print jobrecord['summary']
                if "details" not in jobrecord:
                    jobrecord['details']="null"
                elif jobrecord["details"] is None  or jobrecord["details"]=="":
                    jobrecord['details']="null"

                #print jobrecord['details']
                if "jobtype" not in jobrecord:
                    jobrecord['jobtype']="null"
                elif jobrecord["jobtype"] is None or jobrecord["jobtype"]=="":
                    jobrecord['jobtype']="null"

                #print jobrecord['jobtype']
                jobrecord['id']=JobCrawlerSettings.return_job_record_id(jobrecord)


                #checking if there was error in data
                # if the data will ne None then there is some change in site
                # so we need to update the fields
                error=False
                Fields=[]
                site=jobrecord["site"]
                if jobrecord["title"] is None or jobrecord["title"]=="":
                    error=True
                    Fields.append("title")
                if jobrecord["link"] is None or jobrecord["link"]=="":
                    error=True
                    Fields.append("link")
                if jobrecord["company"] is None or jobrecord["company"]=="":
                    error=True
                    Fields.append("company")
                if jobrecord["time"] is None or jobrecord["time"]=="":
                    error=True
                    Fields.append("time")
                if error:
                    allfields=' '.join(Fields)
                    send_email("crawler error",site,Fields)
                else:
                    #print jobrecord
                    #now add job record to dynamodb
                    #
                    directory=JobCrawlerSettings.databaseDir+jobrecord["site"]
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    #check if the current record already exists
                    if not JobCrawlerSettings.check_job_record_id(jobrecord["site"],jobrecord['id']):
                        total_records=total_records+1
                        last_job_id=jobrecord['id']
                        # adding record to dynamodb
                        add_job_record(jobrecord)
                        #saving database locally (for uniqueness of records)
                        with open(directory+"/"+jobrecord['id']+".json", 'w') as outfile:
                            json.dump(jobrecord, outfile)
                        time.sleep(MAX_WAIT_TIME)
                        print("waiting t requests")

            statdata={}
            if os.path.isfile(JobCrawlerSettings.statsFile):
                with open(JobCrawlerSettings.statsFile) as stat_file:
                    statdata = json.load(stat_file)
                    if category_hash not in statdata:
                        statdata[category_hash]={}
                        statdata[category_hash]["total_scrap_items"]=0
                        statdata[category_hash]["times_scraped"]=0
                    if total_records>0:
                        statdata[category_hash]["last_id"]=last_job_id
                    statdata[category_hash]["last_scrap_items"]=total_records
                    statdata[category_hash]["total_scrap_items"]=statdata[category_hash]["total_scrap_items"]+total_records
                    statdata[category_hash]["times_scraped"]=statdata[category_hash]["times_scraped"]+1
            else:
                statdata[category_hash]={}
                statdata[category_hash]["last_id"]=last_job_id
                statdata[category_hash]["last_scrap_items"]=total_records
                statdata[category_hash]["total_scrap_items"]=total_records
                statdata[category_hash]["times_scraped"]=1



            with open(JobCrawlerSettings.statsFile, 'w') as stat_file:
                json.dump(statdata, stat_file)
            print("Total records added to database: {} ".format(total_records))


if __name__ == "__main__":
    read_update_job_db()
