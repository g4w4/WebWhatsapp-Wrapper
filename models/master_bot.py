import os, sys, time, json
import shutil
import traceback
from uuid import uuid4
from webwhatsapi import WhatsAPIDriver
from webwhatsapi.objects.message import Message, MediaMessage
import config
from Utils import logs
from models import _wapi,observable

from interfaces import interface_messages
from threading import Thread
from Utils import logs

class NewMessageObserver():
    
    driver = None

    def __init__(self,driver): 
        self.driver = driver

    def on_message_received(self, new_messages):   
        for message in new_messages:
            print(message._js_obj.get('chat').get('id').get('_serialized'))
            print(message.content)
            print(message.type)
            print(message)

class start():
    driver = None
    listening = False

    def __init__(self):
        self.driver = WhatsAPIDriver(profile=config.pathSession, client='remote', command_executor=config.selemiunIP)

    def initSession(self):
        try:
            if self.driver.is_logged_in():
                return True
            else :
                name = _wapi.getQrCode(self.driver)
                startSession = Thread(target=self.waitSession)
                startSession.start()
                return name
        except Exception :
            logs.logError('Master-bot initSession',traceback.format_exc())
            return False


    def waitSession(self):
        try:
            logs.logError('Master-bot ','Esprando session')
            _wapi.waitLogin(self.driver)
            self.loopMessages()
            logs.logError('Master-bot ','Session completa')
        except Exception:
            logs.logError('Master-bot Session fallida',traceback.format_exc())
        


    def loopMessages(self):
        self.driver.subscribe_new_messages(NewMessageObserver(self.driver))


