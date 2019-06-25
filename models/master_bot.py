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

_MessagesResponses = {
    "000" : "Hola en que podemos ayudarte \n1. Ver información de orden de compra \n2. Enviar una factura \n3. Hablar con un asesor",
    "001" : "Discupa no entendi tu respuesta puedes repetirla\n1. Ver fecha de pedidos \n2. Enviar una factura \n3. Hablar con un asesor ",
    "1" : "Ingresa tu orden de compra con despacho ej compra-despacho",
    "2" : "Ingresa tu folio de factura",
    "3" : "Lo sentimos no tenemos asesor disponible"
}



class NewMessageObserver():
    
    driver = None
    _Ids = []
    _IdPedido = {}

    def __init__(self,driver): 
        logs.logError('Master-bot ','Loop init')
        self.driver = driver

    def on_message_received(self, new_messages):   
        for message in new_messages:
            getResponse = self.Bot(message.content,message._js_obj.get('chat').get('id').get('_serialized'))
            if getResponse == None :
                self.driver.send_message_to_id(message._js_obj.get('chat').get('id').get('_serialized'),_MessagesResponses["000"])
            else :
                self.driver.send_message_to_id(message._js_obj.get('chat').get('id').get('_serialized'),getResponse)


    def Bot(self,keyWord,id):
        try:
            print(keyWord)
            print(id)
            if self._IdPedido.get(id,False) == False:
                if id not in self._Ids:
                    self._Ids.append(id)
                    return _MessagesResponses.get(keyWord,_MessagesResponses["000"])
                else : 
                    if _MessagesResponses.get(keyWord,False) == False:
                        _MessagesResponses.get(keyWord,_MessagesResponses["001"])
                    else :
                        self._IdPedido[id] = keyWord
                        return _MessagesResponses.get(keyWord,_MessagesResponses["001"])
            else : 
                if self._IdPedido.get(id) == "1" :
                    del self._IdPedido[id]
                    print(self._IdPedido,"--1")
                    return "Tu Orden es tal"
                elif  self._IdPedido.get(id) == "2":
                    del self._IdPedido[id]
                    print(self._IdPedido,"--2")
                    return "Tu factura es esta"
                else :
                    del self._IdPedido[id]
                    print(self._IdPedido,"--3")
                    return _MessagesResponses.get(keyWord,_MessagesResponses["001"])
                 
        except Exception :
            logs.logError('Master-bot initSession',traceback.format_exc())
            return _MessagesResponses["001"]


class start():
    driver = None
    listening = False

    def __init__(self):
        self.driver = WhatsAPIDriver(profile=config.pathSession, client='remote', command_executor=config.selemiunIP)

    def initSession(self):
        try:
            if self.driver.is_logged_in():
                if self.listening :
                    logs.logError('Master-bot ','Session completa')
                else :
                    startSession = Thread(target=self.waitSession)
                    startSession.start()
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
            self.listening = True
            logs.logError('Master-bot ','Esprando session')
            _wapi.waitLogin(self.driver,None)
            self.driver.subscribe_new_messages(NewMessageObserver(self.driver))
            logs.logError('Master-bot ','Session completa _1')
        except Exception:
            logs.logError('Master-bot Session fallida',traceback.format_exc())
        


    def loopMessages(self):
        print("?¿")
        self.driver.subscribe_new_messages(NewMessageObserver(self.driver))


