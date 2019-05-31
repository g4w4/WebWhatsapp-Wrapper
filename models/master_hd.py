import os, sys, time, json
import shutil
import traceback
from webwhatsapi import WhatsAPIDriver
from webwhatsapi.objects.message import Message, MediaMessage
import config
from Utils import logs
from models import _wapi


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

                # # Send messages old #
                # oldMessges = Thread(target=getOldMessages)
                # oldMessges.start()
            
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