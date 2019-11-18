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
    sessionStart = False
    messagesStore = {}

    def __init__(self,socket): 
        if not os.path.exists(config.pathSession): os.makedirs(config.pathSession)
        self.socketIO = socket

    def on_connect(self,*args):
        logs.logError('Socket-Info','Connection whit server')
        self.socketIO.emit('Auth',config.token)

    def on_welcome(self,*args):
        try:
            #print( args[0].get('messages').get('5215587156@c.us','9171') )
            self.messagesStore =  args[0].get('messages')
            #self.messagesStore =  {}
            logs.logError(self.__Keyword,'Connection success')
            if self.driver != None and self.driver.is_logged_in():
                # Is reconnection send all data #
                self.socketIO.emit('change',_wapi.getGeneralInfo(self.driver))
                logs.logError(self.__Keyword,'startThreads')
                self.startThreads( self.messagesStore, self.socketIO )
                #self.startThreads( {} , self.socketIO )
            else:
                # It's the first connection, try to remember session #
                self.socketIO.emit('change',{"whatsAppJoin":False,"accountDown":False})
                self.driver = WhatsAPIDriver(profile=config.pathSession, client='remote', command_executor=config.selemiunIP)
                logs.logError(self.__Keyword,'Check if have cache')
                rember = _wapi.rememberSession(self.driver,self.socketIO)
                logs.logError(self.__Keyword,'Cache is {}'.format(rember))
                if rember :     
                    self.startThreads( self.messagesStore, self.socketIO )
                    #self.startThreads( {}, self.socketIO )
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
            logs.logError(self.__Keyword,'on getQr')
            if self.driver == None :
                self.driver = WhatsAPIDriver(profile=config.pathSession, client='remote', command_executor=config.selemiunIP)
            if self.driver.is_logged_in():
                logs.logError(self.__Keyword,'session started') 
                self.socketIO.emit('change',{'whatsAppJoin':True,'accountDown':False})
                self.socketIO.emit('sendQr', {'socketId':args[0],'error':'The session is started'} )

                # If not detect session #
                if self.sessionStart == False:
                    self.startThreads( self.messagesStore , self.socketIO )

            else :
                logs.logError(self.__Keyword,'go to qr')
                name = _wapi.getQrCode(self.driver)
                logs.logError(self.__Keyword,'send qr')
                self.socketIO.emit('sendQr',{'socketId':args[0],'file':str(name)})
                session = _wapi.waitLogin(self.driver,self.socketIO)

                if session :
                    # Start theads #
                    logs.logError(self.__Keyword,'startThreads')
                    self.socketIO.emit('change',_wapi.getGeneralInfo(self.driver))
                    self.socketIO.emit('receiverLogin',args[0])
                    self.startThreads( self.messagesStore , self.socketIO )
                else :
                    logs.logError(self.__Keyword,'Session down')
                    # ALERT #

        except Exception :
            self.socketIO.emit('sendQr', {'socketId':args[0],'error':traceback.format_exc()} )
            logs.logError(self.__Keyword,traceback.format_exc())

    def on_giveScreen(self,*args):
        screen = Thread(target=_wapi.getScreen,args=(self.driver,self.socketIO,args[0]))
        screen.start()

    def on_sendText(self,*args):
        id = args[0][0]
        message = args[0][1]
        send = Thread(target=_wapi.sendText,args=(self.driver,self.socketIO,id,message))
        send.start()


    def on_sendMessageGroup(self,*args):
        send = Thread(target=_wapi.sendText,args=(self.driver,self.socketIO,config.groupId,'I am here'))
        send.start()

    def on_sendFile(self,*args):
        id = args[0][0]
        caption = args[0][1]
        typeMessage = args[0][2]
        fileMessage = args[0][3]
        send = Thread(target=_wapi.sendFile,args=(self.driver,self.socketIO,id,caption,typeMessage,fileMessage))
        send.start()

    def on_deleteChat(self,*args):
        delChat = Thread(target=_wapi.deleteChat,args=(self.driver,args[0],))
        delChat.start()

    def startThreads(self,*args):
        try:
            oldMessges = Thread(target=self.sincGetOldMessages,args=(args[0],args[1]))
            oldMessges.start()

            if self.sessionStart == False:
                self.sessionStart = True
                logs.logError(self.__Keyword,'Init event loop')
            
                loop = Thread(target=_wapi.loopStatus,args=(self.driver,self.socketIO))
                loop.start()

                self.driver.subscribe_new_messages(observable.NewMessageObserver(self.socketIO,self.driver))
        except Exception:
            logs.logError(self.__Keyword,traceback.format_exc())
            # Alert #

    def sincGetOldMessages(self,*args):
        chats = _wapi.getOldMessages(self.driver,args[0],args[1])
        self.socketIO.emit('oldMessages',chats)


    def on_isValid(self,*args):
        id = args[0][0]
        valid = Thread(target=_wapi.isValid,args=(self.driver,self.socketIO,id))
        valid.start()

    def on_blockNumber(self,*args):
        id = args[0][0]
        print('Bloqueo de numero'+ id)
        valid = Thread(target=_wapi.blockNumber,args=(self.driver,self.socketIO,id))
        valid.start()

        
        