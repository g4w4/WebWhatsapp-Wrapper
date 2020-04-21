import requests
from Utils import logs
import os, sys, time, json
import shutil
import traceback
from uuid import uuid4
from threading import Thread
from services import config
from interfaces import interface_messages


__DOCUMENT_TYPE = {
    'document' : 'document',
    'image' : 'image',
    'video' : 'video',
    'audio' : 'audio',
    'ptt' : 'ptt',
    'chat' : 'chat'
}


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
            driver.wait_for_login(60)
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
        driver.reload_api()
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
            logs.logError('_wapi --> getGeneralInfo','DIVER NOT FOUND')
            return False
        else :
            return {
                "whatsAppJoin" : driver.is_connected(),
                "bateryLevel" : driver.get_battery_level(),
                "numero" : driver.get_phone_number()
            }
    except Exception :
        logs.logError('_wapi --> getGeneralInfo',traceback.format_exc())
        return False
        

####################### getOldMessages(driver) #######################
# Desc : Get general info of account connected                       #
# Params : driver obj                                                #       
# Return :  { ObjChats ... } #                          
# Last Update : 27-06-19                                             #
# By : g4w4                                                          #
######################################################################
def getOldMessages(driver,messages_save,socket):
    try:
         
        chats = {}

        logs.logError('_messages --> getOldMessages','Get all chats')
        _allChats = driver.get_chats_whit_messages()

        print("Esto tengo yo")
        print( messages_save )
        
        for chat in _allChats:
            try:
                idChat = str(chat.get('id'))

                if messages_save.get(idChat,False) != False:
                    print("si esta")
                    x = driver.chat_load_all_earlier_messages(idChat)
                    _messages = driver.get_all_messages_in_chat(idChat,True)

                    #Count messages#
                    i = 0
                    for message in _messages:
                        i= i + 1
                    
                    print("Mensajes")
                    print(idChat)
                    print( i )
                    print(messages_save.get(idChat,False))
                    print(idChat)

                    if i != messages_save.get(idChat,False):
                        print("netro aqui")
                        b = 0
                        x = driver.chat_load_all_earlier_messages(idChat)
                        _messages = driver.get_all_messages_in_chat(idChat,True)
                        for message in _messages:
                            b=b+1
                            print(b)
                            print( messages_save.get(idChat,False) )
                            print(b > messages_save.get(idChat,False))
                            if b > messages_save.get(idChat,False) :
                                try:    
                                    if  message._js_obj['type'] == "location":
                                        _message = interface_messages.getLocation( message, driver)
                                        print("mando mensaje")
                                        print(_message)
                                        if _message != None:
                                            socket.emit('newMessage',_message)
                                    else:
                                        _message = interface_messages.getFormat(message,driver)
                                        print("mando mensaje")
                                        print(_message)
                                        if _message != None:
                                            socket.emit('newMessage',_message)
                                except Exception :
                                    logs.logError('for message in _messages --> getOldMessages',traceback.format_exc())
                else :

                    chats[idChat] = []

                    logs.logError('_messages --> getOldMessages','Get all messages of chat')
                    x = driver.chat_load_all_earlier_messages(idChat)
                    _messages = driver.get_all_messages_in_chat(idChat,True)
                
                    for message in _messages:

                        try:    
                            if message.type == "location":
                                body = interface_messages.getLocation(message,driver)
                                if body != None :
                                    chats[idChat].append(body)
                            else :
                                body = interface_messages.getFormat(message,driver)

                                if body.get('type','') != 'txt':
                                    print( body )

                                if body != None :
                                    chats[idChat].append(body)
                        except Exception :
                            logs.logError('for message in _messages --> getOldMessages',traceback.format_exc())

            except Exception :
                logs.logError('for driver.get_chats_whit_messages()--> getOldMessages',traceback.format_exc())

        logs.logError('_messages --> getOldMessages','Termino')
        return chats
    except Exception :
        #logs.logError('_messages --> getOldMessages',traceback.format_exc())
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
            time.sleep(360)
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
        id_chat = id
        result = driver.send_message_to_id(id_chat,message)
        if result == False:
            print(result)
            id_chat = '52{}'.format(str(id_chat)[-15:len(str(id_chat))])
            driver.send_message_to_id(id_chat,message)
        driver.chat_send_seen(id_chat)
        logs.logError('_wapi --> sendText ---> ',id_chat)
        socketIO.emit('newMessage',interface_messages.getFormatText(message,id))
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
        logs.logError('_wapi --> Sending File '+typeMessage,'')

        s = driver.send_media("{}{}".format(config.pathFiles,fileMessage),id,caption)
        driver.chat_send_seen(id)
        logs.logError('_wapi --> Send File end',s)
        socketIO.emit('newMessage', interface_messages.getFormatFile(fileMessage,id,typeMessage,caption) )
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
        logs.logError("_wapi --> deleteChat","Delete Chat {}".format(id))
        driver.delete_chat(str(id))
    except Exception :
        try:
            logs.logError("_wapi --> deleteChat","Delete Chat {}".format(id))
            new_format = '52{}'.format(str(id)[-15:len(str(id))])
            print( new_format )
            driver.delete_chat( new_format )
        except Exception :
            telegram.telegram("Error deleteChat {}".format(traceback.format_exc()))
            logs.logError('_wapi --> deleteChat',traceback.format_exc())


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
        logs.logError('_wapi --> getScreen Error',traceback.format_exc())
        # Alert # 

# Return if is valid the number
def isValid(driver,socketIO,number):
    try:
        print(number)
        numberWhatsApp = "521{}@c.us".format(number.get('number'))
        isValid = driver.check_number_status(numberWhatsApp)
        print( isValid )
        number['whats_in'] = isValid.status
        #socketIO.emit('validQuery', number)
        print("EMITIO")

        url = "https://ws-voices.com.mx:3001/resultQuery"

        payload = number
        headers = { 'Content-Type': "application/x-www-form-urlencoded", }

        response = requests.request("POST", url, data=payload, headers=headers)

        print(response.text)

    except Exception :
        print("FALLO")
        if "TypeError: <NumberStatus -" in traceback.format_exc() :
            socketIO.emit('validQuery', {'isValid':"400",'number':number} )
        else :
            logs.logError('Master-API',traceback.format_exc())
            socketIO.emit('validQuery', {'isValid':"400",'number':number} )
            return False

# Blocked number
def blockNumber(driver,socketIO,number):
    try:
        driver.contact_block(number)
        socketIO.emit('successBlocked', number)
    except Exception :
        if "TypeError: <NumberStatus -" in traceback.format_exc() :
            socketIO.emit('validQuery', {'isValid':"400",'number':number} )
        else :
            logs.logError('Master-API',traceback.format_exc())
            return False
