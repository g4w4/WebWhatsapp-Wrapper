#!/usr/bin/env python3

from webwhatsapi import WhatsAPIDriver
from webwhatsapi.objects.message import Message, MediaMessage
from configPath import selemiunIP,pathCache
import traceback
import shutil
import datetime
from Utils import logs

############################ Con(driver) ########################
# Desc : connect whit browser                                   #
# Params :                                                      #       
# Return : False or driver arrayFunctions['wapi_functions']     #
# Last Update : 30-05-19 g4w4                                   #
# By : g4w4                                                     #
#################################################################
def con(driver = None):
    try:
       driver = WhatsAPIDriver(profile=pathCache, client='remote', command_executor=selemiunIP)
       return driver
    except Exception as e:
        logs.logError('Selenium --> con',traceback.format_exc())
        return False
    