from Utils import logs
import os, sys, time, json
import shutil
import traceback
from uuid import uuid4
from services import config
from interfaces import interface_messages


############################ rememberSession(driver) ############
# Desc : wait for session                                       #
# Params : driver obj                                           #       
# Return :  Boolean                                              #
# Last Update : 30-05-19                                        #
# By : g4w4                                                     #
#################################################################
def rememberSession(driver,socket):
    try:
        if driver is None :
            return False
        else :
            driver.wait_for_login(40)
            if driver.is_logged_in():
                socket.emit('change',getGeneralInfo(driver))
    except Exception :
        logs.logError('Selenium --> rememberSession',traceback.format_exc())
        # Alert #


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
                idName = uuid4().hex
                name = "{}{}".format(config.pathFiles,idName+'.png') 
                if os.path.exists(name) : os.remove(name)
                driver.get_qr(name)

                return idName
            
    except Exception :
        logs.logError('_wapi --> getQrCode',traceback.format_exc())
        return False


############################ waitLogin(driver) ##################
# Desc : wait init session                                      #
# Params : driver obj                                           #       
# Return :  Boolean                                             #
# Last Update : 30-05-19                                        #
# By : g4w4                                                     #
#################################################################
def waitLogin(driver,socketId):
    try:
        driver.wait_for_login()
        driver.save_firefox_profile()
        return True
    except Exception :
        logs.logError("_wapi --> waitLogin",traceback.format_exc())
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
        logs.logError('_messages --> getOldMessages',traceback.format_exc())
        return False


def loopStatus(driver,socketIO):
    try:
        while driver != None:
            time.sleep(60)
            logs.logError('_messages --> loopStatus','Send account info')
            socketIO.emit('change',getGeneralInfo(driver))
    except Exception :
        logs.logError('_messages --> loopStatus',traceback.format_exc())
        # Alert #
            
   