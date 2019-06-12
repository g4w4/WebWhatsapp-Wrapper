import os, sys, time, json
import shutil
import traceback
from uuid import uuid4
from threading import Thread
from webwhatsapi import WhatsAPIDriver
from webwhatsapi.objects.message import Message, MediaMessage
import configAPI
from Utils import logs
from models import _wapi

_Responses = {
    "003" : { "code" : "003" , "desc" : "Desconectado" },
    "200" : { "code" : 200, "desc" : "Completado" , "data" : None },
    "201" : { "code" : 200, "desc" : "success", "data" : "The session is active"},
    "202" : { "code" : 200, "desc": "Completado", "data": { "desc": "Mensaje Enviado", "status": "success" } },
    "203" : { "code" : 200, "desc" : "Completado" , "data" : "Numero valido" },
    "404" : { "code" : 404, "desc": "Completado", "data": "Numero no valido" },
    "500" : { "code" : 500, "desc" : "Error interno", "data" : "Internal error"},
    "501" : { "code" : 200, "desc": "Completado", "data": { "desc": "Chat no existe", "status": "error" } }
}

_MessageError = {
    "Selenium" : "Selenium no connected is required restart",
    "QrCode" : "Not found code Qr",
    "Wait" : "Session not achieved",
    "Screen" : "Screen failed",
    "ChatList" : "Not get chat list",
    "SendMessage" : "Failed send message",
    "RestartSuccess" : "API restarted"
}

class start():
    driver = None

    def __init__(self):
        try:
            self.driver = WhatsAPIDriver(profile=configAPI.pathSession, client='remote', command_executor=configAPI.selemiunIP)
            logs.logError('Master-API',"WhatsApp on")
            loop = Thread(target=self.loopSession)
            loop.start()
        except Exception:
            logs.logError('Master-API',traceback.format_exc())
            logs.sendMailError(_MessageError["Selenium"])

    def getQr(self):
        try:
            if self.driver.is_logged_in():
                return _Responses["201"] 
            else :
                qr = _wapi.getQrCode(self.driver)
                loop = Thread(target=self.waitSession)
                loop.start()
                return qr
        except Exception :
            logs.logError('Master-API',traceback.format_exc())
            logs.sendMailError(_MessageError["QrCode"])
            return _Responses["500"] 

    def waitSession(self):
        try:
            self.driver.wait_for_login()
            logs.logError('Master-API',"Session Start")
            self.driver.save_firefox_profile()
        except Exception :
            logs.sendMailError(_MessageError["Wait"])
            logs.logError('Master-API',traceback.format_exc())

    def getScreen(self):
        try:
            screen = _wapi.getScreenApi(self.driver)
            return screen
        except Exception :
            logs.logError('Master-API',traceback.format_exc())
            logs.sendMailError(_MessageError["Screen"])
            return _Responses["500"] 

    def loopSession(self):
        time.sleep(30)
        firts = True
        while(True):
            try:
                if firts :
                    logs.sendMailError(_MessageError["RestartSuccess"])
                    firts = False
                else : 
                    firts = False
                    session = self.driver.is_logged_in()
                    logs.logError('Master-API',"Session on {}".format(session))
                    time.sleep(60)
            except Exception :
                logs.logError('Master-API',traceback.format_exc())
                logs.sendMailError(_MessageError["Selenium"])

    def getChatList(self):
        try:
            wsp = _Responses["200"]
            if self.driver.is_logged_in():
                contacts = []
                for ids in self.driver.get_all_chat_ids():
                    con = self.driver.get_chat_from_id( str(ids) )
                    contacts.append( {'ID':str(ids),"info":str(con).replace("<","").replace(">","")} )
                wsp['data'] = contacts
                return wsp
            else:
                return _Responses["003"]
        except Exception :
            logs.logError('Master-API',traceback.format_exc())
            logs.sendMailError(_MessageError["ChatList"])
            return _Responses["500"] 

    def sendMessage(self,idChat,message):
        try:
            # chat = self.driver.get_chat_from_id(str(idChat))
            # if chat :
            print(idChat)
            print(message)
            self.driver.send_message_to_id(str(idChat),message)
            print("fin")
            return _Responses["202"]
            # else:
            #     return _Responses["501"]
        except Exception :
            if "raise ChatNotFoundError" in traceback.format_exc() :
                return _Responses["501"]
            else :
                logs.logError('Master-API',traceback.format_exc())
                logs.sendMailError(_MessageError["SendMessage"])
                return _Responses["500"] 

    def isValid(self,number):
        try:
            numberWhatsApp = "521{}@c.us".format(number)
            isValid = self.driver.check_number_status(numberWhatsApp)
            return _Responses["203"] if isValid.status == 200 else _Responses["404"]
        except Exception :
            if "TypeError: <NumberStatus -" in traceback.format_exc() :
                return _Responses["404"] 
            else :
                logs.logError('Master-API',traceback.format_exc())
                return _Responses["500"] 


            