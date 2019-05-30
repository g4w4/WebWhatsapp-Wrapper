#!/usr/bin/env python3

import os, sys, time, json
import shutil
import traceback
from uuid import uuid4
from threading import Thread
from configPath import testPath

# master path #
sys.path.insert(0,testPath)

# Import wapi #
from webwhatsapi import WhatsAPIDriver
from webwhatsapi.objects.message import Message, MediaMessage

# modules system #
from models import _selenium,_wapi,observable

# Variables #
driver = None

print("Start v2.0.0")

print("Connection to selenium")

driver = _selenium.con()

print("Check if have cache")
sessionOn = _wapi.rememberSession(driver)

print("Session is {}".format(sessionOn))

if sessionOn == False :
    print("Get qr code")
    qrName = _wapi.getQrCode(driver)

    print("Le name file is {}",qrName)
    if isinstance(qrName, str) :
        driver.wait_for_login(40)
        driver.save_firefox_profile(True)
    else :
        print("session failed")

print("Session success")

print("General info of account")
print(_wapi.getGeneralInfo(driver))

print("Get all chats")
print(_wapi.getOldMessages(driver))

print("Start lisener of new messages")
driver.subscribe_new_messages(observable.NewMessageObserver("test",driver))

    


