import os
import hashlib

# defined Crawler settings
class JobCrawlerSettings():
    # define the fields for your item here like:
    # name = scrapy.Field()
    sites            =['monster',"juju"]
    catoutputfiles         ={
                            "monster":{"file":"monster_cat.json","format":"json"},
                            "juju":{"file":"juju_cat.json","format":"json"}
                        }
    outputdir       ="cache/"
    processDir      ="proc/"
    databaseDir     ="database/"
    statsFile       ="database/stats.json"
    joboutputdir    = "cache/jobs/"
    processFileExt       =".proc"
    site_cat_file       ="categories.json"
    error_log_file       ="error_log.json"
    allowed_domains     =[
                        "www.monster.com",
                        "job-openings.monster.com",
                        "jobview.monster.com",
                        "www.techcareers.com",
                        "www.juju.com"
                            ]
    crawlerCatDB        ={
                            "http://www.juju.com/category/":{
                                0:{
                                    "catname":"Jobs by category",
                                    "looper":{
                                            "containercss":'article.content div.cols_block_3 div ul li',
                                            "cattext":"a::text",
                                            "caturl":"a::attr(href)",
                                            "domainappend":1
                                        }
                                }
                            },
                            "https://www.monster.com/jobs/":{
                                "superloop":"div.section.top-jobs-section div.row div.caption",
                                "catname":'h3::text',
                                "looper":{
                                            "containercss":'ul.card-columns li',
                                            "cattext":"a::text",
                                            "caturl":"a::attr(href)",
                                            "domainappend":0
                                        }
                                }
                        }
    crawlerMainDB       ={
                            "cat1":{
                                0:{
                                    "item":{
                                            "containercss":'div.article div ul.job_results li dl.job',
                                            "jobtitle":{"css":"dt p a::text","type":"unicode"},
                                            "joblink":{"css":"dt p a::attr(href)","type":"text"},
                                            "jobsite":"juju",
                                            "jobcompany":{"css":"dd.company::text","type":"before_paran"},
                                            "joblocation":{"css":"dd.company::text","type":"within_paran"},
                                            "jobtime":{"css":"dd.options div.source::text","type":"within_paran"},
                                            "domainappend":0
                                        },
                                    "nextpage":"ul.pagelinks li a[title='Next Page']::attr(href)",
                                    "nextdomainappend":1,
                                    "timeformat":"%m/%d/%y"
                                }
                            }

                        }
    crawlerCatLinks     ={
                            "http://www.juju.com":{
                                "category":"cat1"
                            }
                        }
    standardTimeFormat  ="%m/%d/%y"

    @staticmethod
    def extract_before_paran(text):
                    return text.split(" (",1)[0].strip()

    @staticmethod
    def extract_within_paran(text):
                    return text.split(" (")[-1].split(")")[0].strip()
    @staticmethod
    def convert_unicode(text):
                    return text.strip()

    @staticmethod
    def return_ext_attr(text,typ):
                if typ=="before_paran":
                    return JobCrawlerSettings.extract_before_paran(text)
                elif typ=="within_paran":
                    return JobCrawlerSettings.extract_within_paran(text)
                elif typ=="unicode":
                    return JobCrawlerSettings.convert_unicode(text)
                else:
                    return text.strip()
    @staticmethod
    def return_job_record_id(jobrecord):
        stringhsh=JobCrawlerSettings.convert_unicode(jobrecord["time"])+JobCrawlerSettings.convert_unicode(jobrecord["company"])+JobCrawlerSettings.convert_unicode(jobrecord["title"])
        hashStr=hashlib.md5(stringhsh.encode('utf-8')).hexdigest()
        return hashStr

    @staticmethod
    def check_job_record_id(site,id):
        if os.path.isfile(JobCrawlerSettings.databaseDir+site+"/"+id+".json"):
            return True
        else:
            return False
