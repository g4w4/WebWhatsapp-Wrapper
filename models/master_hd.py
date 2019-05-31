import os, sys, time, json
import shutil
import traceback
from uuid import uuid4
from threading import Thread
from webwhatsapi import WhatsAPIDriver
from webwhatsapi.objects.message import Message, MediaMessage
import config
from Utils import logs
from models import _wapi,observable


class start():
    socketIO = None
    wsp = None
    driver = None
    awaitLogin = None
    __Keyword = "Master-Info"

    def __init__(self,socket): 
        if not os.path.exists(config.pathSession): os.makedirs(config.pathSession)
        self.socketIO = socket

    def on_connect(self,*args):
        logs.logError('Socket-Info','Connection whit server')
        self.socketIO.emit('Auth',config.token)

    def on_welcome(self,*args):
        try:
            logs.logError(self.__Keyword,'Connection success')
            if self.driver != None and self.driver.is_logged_in():
                # Is reconnection send all data #
                self.socketIO.emit('change',_wapi.getGeneralInfo(self.driver))
                logs.logError(self.__Keyword,'startThreads')
                self.startThreads()
            else:
                # It's the first connection, try to remember session #
                self.socketIO.emit('change',{"whatsAppJoin":False,"accountDown":False})
                self.driver = WhatsAPIDriver(profile=config.pathSession, client='remote', command_executor=config.selemiunIP)
                logs.logError(self.__Keyword,'Check if have cache')
                rember = _wapi.rememberSession(self.driver)

                if rember :
                    self.socketIO.emit('change',_wapi.getGeneralInfo(self.driver))
                else : 
                    logs.logError(self.__Keyword,'Session down')
                    # ALERT #


        except Exception :
            logs.logError('Master-Error',traceback.format_exc())
            # ALERTA #

    def on_disconnect(self,*args):
        logs.logError(self.__Keyword,'Connection end')

    def on_reconnect(self,*args):
        logs.logError(self.__Keyword,'Connection reconnect')
        self.socketIO.emit('Auth',config.token)

    def on_getQr(self,*args):
        try:
            if self.driver == None :
                self.driver = WhatsAPIDriver(profile=config.pathSession, client='remote', command_executor=config.selemiunIP)
            if self.driver.is_logged_in():
                logs.logError(self.__Keyword,'session started') 
                self.socketIO.emit('change',{'whatsAppJoin':True,'accountDown':False})
                self.socketIO.emit('sendQr', {'socketId':args[0],'error':'The session is started'} )
            else :
                logs.logError(self.__Keyword,'go to qr')
                name = _wapi.getQrCode(self.driver)
                logs.logError(self.__Keyword,'send qr')
                self.socketIO.emit('sendQr',{'socketId':args[0],'file':str(name)})
                session = _wapi.waitLogin()

                if session :
                    # Start theads #
                    logs.logError(self.__Keyword,'startThreads')
                    self.socketIO.emit('change',_wapi.getGeneralInfo(self.driver))
                    self.socketIO.emit('receiverLogin',args[0])
                    self.startThreads()
                else :
                    logs.logError(self.__Keyword,'Session down')
                    # ALERT #

        except Exception :
            self.socketIO.emit('sendQr', {'socketId':args[0],'error':traceback.format_exc()} )
            logs.logError(self.__Keyword,traceback.format_exc())

    def startThreads(self):
        try:
            logs.logError(self.__Keyword,'Init event loop')
        
            loop = Thread(target=_wapi.loopStatus,args=(self.driver,self.socketIO))
            loop.start()

            oldMessges = Thread(target=self.sincGetOldMessages)
            oldMessges.start()

            self.driver.subscribe_new_messages(observable.NewMessageObserver(self.socketIO,self.driver))
        except Exception:
            logs.logError(self.__Keyword,traceback.format_exc())
            # Alert #

    def sincGetOldMessages(self):
        chats = _wapi.getOldMessages(self.driver)
        self.socketIO.emit('oldMessages',chats)

        
        