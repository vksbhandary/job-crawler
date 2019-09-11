

import scrapy


class JobCrawlerSettings():
    # define the fields for your item here like:
    # name = scrapy.Field()
    crawlers            =['monster','monstercat']
    allowed_domains     =["www.monster.com",
                        "job-openings.monster.com",
                        "jobview.monster.com",
                        "www.techcareers.com"
                            ]
