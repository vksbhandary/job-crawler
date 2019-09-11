# -*- coding: utf-8 -*-
import boto3
import os

#http://docs.aws.amazon.com/amazondynamodb/latest/gettingstartedguide/GettingStarted.Python.03.html
def add_job_record(data):
    print(data)
    dynamodb = boto3.resource('dynamodb',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY'],
        aws_secret_access_key=os.environ['AWS_ACCESS_PASS'],
        region_name=os.environ['AWS_REGION']
        )
    table = dynamodb.Table('jobsdb')
    response = table.put_item(
       Item={
            'id': data["id"],
            'title': data["title"],
            'company': data["company"],
            'link': data["link"],
            'site': data["site"],
            'summary': data["summary"],
            'details': data["details"],
            'postedon': data["time"],
            'location': data["location"],
            'jobtype': data["jobtype"],
        }
    )
