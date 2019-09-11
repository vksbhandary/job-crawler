import time
#from signal import SIGKILL
import os, shutil
import subprocess
import sys
import socket
import json
#import scrap
from glob import glob
from job_crawler import JobCrawlerSettings

from clean import read_update_job_db

MIN_REPEAT_TIME=1 #in minutes
MAX_PARALLEL_THREADS=1


def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(int(pid), 0)
    except OSError:
        return False
    else:
        return True

def get_lock(process_name):
    # Without holding a reference to our socket somewhere it gets garbage
    # collected when the function exits
    get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    try:
        get_lock._lock_socket.bind('\0' + process_name)
        print ("Locked process: %s"% (process_name))
    except socket.error:
        print 'lock exists'
        sys.exit()

def check_any_running_process():
    running=False
    processes=0
    for file_name in glob(JobCrawlerSettings.processDir+'*'+JobCrawlerSettings.processFileExt):
        pid=file_name.split("/")[-1].split(".")[0]
        if check_pid(pid):
            running=True
            processes=processes+1
        else:
            try:
                os.remove(file_name)
                print("removed PID file "+file_name)
            except OSError:
                pass
    return (running,processes)

def init():
    jobdir=JobCrawlerSettings.joboutputdir
    if os.path.exists(jobdir):
        shutil.rmtree(jobdir)
    os.makedirs(jobdir)


def return_site_data():
    with open(JobCrawlerSettings.site_cat_file) as data:
        catsettingdata = json.load(data)
        return catsettingdata


def main():
    get_lock('Hireslot_scheduler')
    init()
    catsettingdata=return_site_data()
    sitekeys=catsettingdata.keys()
    counter=0
    #print(sitekeys)
    while True:
        #logging.debug("Running scrapper at {}".format(time.time()))
        #print("Running scrapper at {}".format(time.time()))
        running,processes=check_any_running_process()
        if not running and counter+1 > len(sitekeys):
            counter=0
            print("Updating fetched records {}".format(time.time()))
            read_update_job_db()
            print("Finished updating database {}".format(time.time()))
            # call method to update on DB
        elif (running and processes< MAX_PARALLEL_THREADS) or not running:
            #run another process
            print("Running scrapper at {}".format(time.time()))
            site=sitekeys[counter]
            print("Scraping site: "+site)
            subprocess.call(["python", "scrap.py",site])
            counter=counter+1
            #subprocess.Popen([sys.executable, "ls -la"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        else:
            print("crawler still running. Will retry after %d min" % (MIN_REPEAT_TIME))
        #subprocess.call(["ls", "-la"])
        #pid = subprocess.Popen([sys.executable, "ls -la"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE).pid # call subprocess
        #pid = subprocess.Popen("ls -la", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE).pid # call subprocess
        #print pid #subprocess.Popen("ls -la", shell=True, stdout=subprocess.PIPE).stdout.read()

        #sleep for no. of sec
        time.sleep(MIN_REPEAT_TIME*60)


if __name__ == "__main__":
   try:
      main()
   except KeyboardInterrupt:
      # do nothing here
      print("Exiting process.")
      pass
