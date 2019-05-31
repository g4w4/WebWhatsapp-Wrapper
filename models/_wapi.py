from Utils import logs
import os, sys, time, json
import shutil
import traceback
from uuid import uuid4
from config import pathFiles
from interfaces import interface_messages


############################ rememberSession(driver) ############
# Desc : wait for session                                       #
# Params : driver obj                                           #       
# Return :  Boolean                                              #
# Last Update : 30-05-19                                        #
# By : g4w4                                                     #
#################################################################
def rememberSession(driver):
    try:
        if driver is None :
            return False
        else :
            driver.wait_for_login(40)
            return True if driver.is_logged_in() else False
    except Exception as e:
        logs.logError('Selenium --> con',traceback.format_exc())
        return False


############################ getQrCode(driver) ##################
# Desc : Get qr code and save session                           #
# Params : driver obj                                           #       
# Return :  Boolean or dir of qrCod                             #
# Last Update : 30-05-19                                        #
# By : g4w4                                                     #
#################################################################
def getQrCode(driver):
    try:
        if driver is None :
            return False
        else :
            if driver.is_logged_in() : 
                return True
            else:
                name = "{}{}".format(pathFiles,uuid4().hex+'.png') 
                if os.path.exists(name) : os.remove(name)
                driver.get_qr(name)

                return name
            
    except Exception as e:
        logs.logError('_wapi --> getQrCode',traceback.format_exc())
        return False


####################### getGeneralInfo(driver) #######################
# Desc : Get general info of account connected                       #
# Params : driver obj                                                #       
# Return :  obj {whatsAppJoin:Bool,bateryLevel:number,numero:number} #                          #
# Last Update : 30-05-19                                             #
# By : g4w4                                                          #
######################################################################
def getGeneralInfo(driver):
    try:
        if driver is None :
            return False
        else :
            return {
                "whatsAppJoin" : driver.is_logged_in(),
                "bateryLevel" : driver.get_battery_level(),
                "numero" : driver.get_phone_number()
            }
    except Exception as e:
        logs.logError('_wapi --> getGeneralInfo',traceback.format_exc())
        return False
        

####################### getOldMessages(driver) #######################
# Desc : Get general info of account connected                       #
# Params : driver obj                                                #       
# Return :  obj {whatsAppJoin:Bool,bateryLevel:number,numero:number} #                          #
# Last Update : 30-05-19                                             #
# By : g4w4                                                          #
######################################################################
def getOldMessages(driver):
    try:
        chats = {}
        for chat in driver.get_chats_whit_messages():
            idChat = str(chat.get('id'))
            chats[idChat] = []
            _messages = driver.get_all_messages_in_chat(idChat,True)
            for message in _messages:
                body = interface_messages.getFormat(message,driver)
                chats[idChat].append(body)

        return chats
    except Exception :
        logs.logError('_messages --> getMessage',traceback.format_exc())
        return False
            
   