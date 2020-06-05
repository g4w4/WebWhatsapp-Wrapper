import os, sys, time, json
import configAPI
sys.path.insert(0,configAPI.masterPath)
import requests 
from io import BytesIO
import shutil
import traceback
from uuid import uuid4
from threading import Thread
from webwhatsapi import WhatsAPIDriver
from webwhatsapi.objects.message import Message, MediaMessage



number = sys.argv[1]
fullNumber= sys.argv[2]
account=12
namePic=""
	
time.sleep(5)

driver = WhatsAPIDriver(profile=configAPI.pathSession, client='remote', command_executor=configAPI.selemiunIP)

driver.create_chat_by_number(number)

driver.wait_for_login()

isValid = driver.check_number_status(fullNumber)
if isValid.status == 200 :
    objReturn = None
    print( "Result: "+objReturn )
    # pic = driver.get_profile_pic_from_id(fullNumber)
    # if pic != False:
    #     idName = uuid4().hex
    #     name = "{}{}".format(configAPI.pathFiles,idName+'.png')
    #     iioo = BytesIO(pic)
    #     with open(name, "wb") as f:
    #         f.write(iioo.getvalue())
    #     namePic = name
    print( objReturn )
else:
    print(  "Sin WhatsApp" )



  
# # defining the api-endpoint  
# API_ENDPOINT = "http://192.168.0.6:6070/login"
  
#   # data to be sent to api 
# data = {'lastlogin':objReturn, 
#         'number':number, 
#         'account':account,
#         'namePic':namePic } 
  
# # sending post request and saving response as response object 
# r = requests.post(url = API_ENDPOINT, data = data) 
  
# # extracting response text  
# pastebin_url = r.text 
# print(pastebin_url)

driver.close()

