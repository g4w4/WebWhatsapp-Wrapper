import sys
import os.path
import datetime
import requests
from Utils import configUtils
from services import config


def write_log(keyword,data):
    log = "{} : {} --> {}".format(str(datetime.datetime.today()),keyword,data)
    with open(config.masterPath+"logs.txt", 'a+') as f:
        f.write(log+'\n')
        f.close()
    print(log); 

def logError(KeyError,data):
    print("{} : {} --> {}".format(str(datetime.datetime.today()),KeyError,data))
    write_log(KeyError,data)

def sendMailError(error):

    mail = """
    <h1> Error in {} </h1>
    <small>{}</small>
    <p><a href="{}">Restart App</a></p>
    """.format(configUtils.appName,error,configUtils.linkRestart)
    
    payload = { "from" : configUtils.mailFrom,
        "to" : configUtils.mailTo,
        "subject" : configUtils.subject,
        "html" : mail }

    petition = requests.post(configUtils.ip, data=payload)

    return petition
