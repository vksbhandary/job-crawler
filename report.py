import os
import datetime
import smtplib
import json
from job_crawler import JobCrawlerSettings

recieverID="vksbhandary@gmail.com"

def send_email(subject, site, fields):
    goodtogo=True
    logdata=[]
    if not os.path.isfile(JobCrawlerSettings.error_log_file):
        goodtogo=True
    else:
        with open(JobCrawlerSettings.error_log_file) as log_file:
            log = json.load(log_file)
            logdata=log
            currtime = datetime.datetime.now()
            prevtime=log[-1]["time"]
            timediffobj=currtime-prevtime
            if timediffobj.total_seconds()/60 > 60:
                #if one hour is passed since last error
                goodtogo=True
            else:
                goodtogo=False
        if goodtogo:
            currentdata={}
            currentdata["time"]=datetime.datetime.now()
            currentdata["site"]=site
            currentdata["fields"]=fields
            allfields=' '.join(fields)
            logdata.append(currentdata)

            with open(JobCrawlerSettings.error_log_file, 'w') as outfile:
                json.dump(logdata, outfile)

            body="There is some change in "+site+" site's design bot can not access Following fields properly\n\n"+allfields
            gmail_user = os.environ['hireslot_gmail_username']
            gmail_pwd = os.environ['hireslot_gmail_password']
            FROM = os.environ['hireslot_gmail_username']
            #TO = recipient if type(recipient) is list else [recipient]
            TO  = [recieverID]
            SUBJECT = subject
            TEXT = body

            # Prepare actual message
            message = """From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
            try:
                #server = smtplib.SMTP("smtp.gmail.com", 587)
                #server.ehlo()
                #server.starttls()
                #server.login(gmail_user, gmail_pwd)
                #server.sendmail(FROM, TO, message)
                #server.close()
                #print 'successfully sent the mail'

                # SMTP_SSL Example
                server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                server_ssl.ehlo() # optional, called by login()
                server_ssl.login(gmail_user, gmail_pwd)
                # ssl server doesn't support or need tls, so don't call server_ssl.starttls()
                server_ssl.sendmail(FROM, TO, message)
                #server_ssl.quit()
                server_ssl.close()
                print 'successfully sent the mail'
            except:
                print "failed to send mail"



if __name__ == "__main__":
    send_email("error","This is test message")
