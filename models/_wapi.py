from Utils import logs
import os, sys, time, json
import shutil
import traceback
from uuid import uuid4
from threading import Thread
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
            driver.wait_for_login(10)
            if driver.is_logged_in():
                socket.emit('change',getGeneralInfo(driver))
                socket.emit('reboot',"Success")
                return True
    except Exception :
        logs.logError('Selenium --> rememberSession',traceback.format_exc())
        socket.emit('reboot',"Failed")
        return False
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

                return "{}.png".format(idName)
            
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
        driver.wait_for_login(120)
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
# Return :  { ObjChats ... } #                          
# Last Update : 27-06-19                                             #
# By : g4w4                                                          #
######################################################################
def getOldMessages(driver):
    try:
        #Variable return 
        chats = {}

        logs.logError('_messages --> getOldMessages','Get all chats')
        _allChats = driver.get_chats_whit_messages()
        
        for chat in _allChats:
            try:
                idChat = str(chat.get('id'))
                chats[idChat] = []

                logs.logError('_messages --> getOldMessages','Get all messages of chat')
                _messages = driver.get_all_messages_in_chat(idChat,True)

                for message in _messages:
                    try:
                        body = interface_messages.getFormat(message,driver)

                        chats[idChat].append(body)

                    except Exception :
                        logs.logError('for message in _messages --> getOldMessages',traceback.format_exc())

            except Exception :
                logs.logError('for driver.get_chats_whit_messages()--> getOldMessages',traceback.format_exc())

        logs.logError('_messages --> getOldMessages','Termino')
        return chats
    except Exception :
        logs.logError('_messages --> getOldMessages',traceback.format_exc())
        return False


####################### loopStatus(driver) ###########################
# Desc : Send info account to serverSocket                           #
# Params : driver obj , socketIO obj                                 #       
# Return :  loop                                                     #
# Last Update : 30-05-19                                             #
# By : g4w4                                                          #
######################################################################
def loopStatus(driver,socketIO):
    try:
        while driver != None:
            time.sleep(60)
            logs.logError('_messages --> loopStatus','Send account info')
            socketIO.emit('change',getGeneralInfo(driver))
    except Exception :
        logs.logError('_messages --> loopStatus',traceback.format_exc())
        # Alert #


####################### getScreen(driver) ###########################
# Desc : Send picture of status in account                           #
# Params : driver obj , socketIO obj                                 #       
# Return :  emition                                                  #
# Last Update : 30-05-19                                             #
# By : g4w4                                                          #
######################################################################        
def getScreen(driver,socketIO,id):
    try:
        if driver != None:
            logs.logError('_wapi --> getScreen','saving screen')
            idName = uuid4().hex
            name = "{}{}".format(config.pathFiles,idName+'.png')
            if os.path.exists(name) : os.remove(name)
            driver.screenshot(name)
            socketIO.emit('sendScreen',{'socketId':id,'file':"{}.png".format(idName)})
        else:
            socketIO.emit('sendScreen', {'socketId':id,'error':'Browser not connected'} )
    except Exception:
        logs.logError('_wapi --> getScreen',traceback.format_exc())
        socketIO.emit('sendScreen', {'socketId':id,'error':traceback.format_exc()} )
        # Alert # 


####################### sendText(driver,socketIO,id,message) #########
# Desc : Send messages to wsp user                                   #
# Params : driver obj , socketIO obj , id wspId , message String     #       
# Return :  emition                                                  #
# Last Update : 30-05-19                                             #
# By : g4w4                                                          #
######################################################################
def sendText(driver,socketIO,id,message):
    try:
        logs.logError('_wapi --> sendText','send')
        driver.send_message_to_id(id,message)
        driver.chat_send_seen(id)
        socketIO.emit('newMessage',{'chat':id,'message':message,'sendBy':'Agent'})
    except Exception :
        logs.logError('_wapi --> sendText',traceback.format_exc())
        socketIO.emit('errorSendTxt',{'chat':id,'message':message,'sendBy':'Agent'})
        # Alert #


###### sendFile(driver,socketIO,id,caption,typeMessage,fileMessage) ##
# Desc : Send file to wsp user                                       #
# Params : driver obj , socketIO obj , id wspID , caption string,    #
# typeMessage predetermined, fileMessage (src) string                #       
# Return :  emition                                                  #
# Last Update : 30-05-19                                             #
# By : g4w4                                                          #
######################################################################
def sendFile(driver,socketIO,id,caption,typeMessage,fileMessage):
    try:
        logs.logError('_wapi --> Sending File','')
        driver.send_media("{}{}".format(config.pathFiles,fileMessage),id,caption)
        driver.chat_send_seen(id)
        logs.logError('_wapi --> Send File end','')
        socketIO.emit('newMessage',{'chat':id,'message':fileMessage,'type':typeMessage,'caption':caption,'sendBy':'Agent'})
    except Exception :
        logs.logError('_wapi --> sendFile',traceback.format_exc())
        socketIO.emit('errorSendFile',{'chat':id,'message':caption,'sendBy':'Agent'})
        # Alert #


######################## deleteChat(driver,id) #######################
# Desc : Delete all conversation in divece                           #
# Params : driver obj , id wspID                                     #       
# Return :  None                                                     #
# Last Update : 03-06-19                                             #
# By : g4w4                                                          #
######################################################################
def deleteChat(driver,id):
    try:
        logs.logError("_wapi -->","Delete Chat {}".format(id),)
        driver.delete_chat(str(id))
    except Exception :
        logs.logError('_wapi --> sendFile',traceback.format_exc())


####################### getSreenApi(driver) ###########################
# Desc : Send picture of status in account                           #
# Params : driver obj , socketIO obj                                 #       
# Return :  emition                                                  #
# Last Update : 06-06-19                                             #
# By : g4w4                                                          #
######################################################################        
def getScreenApi(driver):
    try:
        logs.logError('_wapi --> getScreen','saving screen')
        idName = uuid4().hex
        name = "{}{}".format(config.pathFiles,idName+'.png')
        if os.path.exists(name) : os.remove(name)
        driver.screenshot(name)
        return idName
    except Exception :
        logs.logError('_wapi --> getScreen',traceback.format_exc())
        # Alert # 