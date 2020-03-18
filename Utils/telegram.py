import sys
import os.path
import datetime
import requests
from Utils import configUtils

def telegram(message):
    payload = { "message": "{} : {}".format(configUtils.accountName,message) }
    petition = requests.post(configUtils.telegram, data=payload)
    return petition