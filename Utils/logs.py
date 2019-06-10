import sys
import os.path
import datetime
import requests
import configUtils


def write_log(keyword,data):
    log = "{} : {} --> {}".format(str(datetime.datetime.today()),keyword,data)
    with open("./logs.txt", 'a+') as f:
        f.write(log+'\n')
        f.close()
    print(log); 

def logError(KeyError,data):
    print("{} : {} --> {}".format(str(datetime.datetime.today()),KeyError,data))

def sendMailError(error):

    mail = """
    <h1> Error in {} </h1>
    <small>{}</small>
    <a href="{}">Restart App</a>
    """.format(configUtils.appName,error,configUtils.linkRestart)
    
    payload = { "from" : configUtils.mailFrom,
        "to" : configUtils.mailTo,
        "subject" : configUtils.subject,
        "html" : mail }

    petition = requests.post(configUtils.ip, data=payload)

    return petition
