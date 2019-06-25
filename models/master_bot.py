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

_Menu = {
    "000" : "Hola en que podemos ayudarte \n1. Consulta de Orden de Compra \n2. Consulta de inventarios en mano \n3. Consulta de artículo",
    "001" : "Discupa no entendi tu respuesta puedes repetirla\n1. Consulta de Orden de Compra \n2. Consulta de inventarios en mano \n3. Consulta de artículo",
    "1" : "Porfavor ingresa tu numero de compra seguido del despacho\nEj. numCompra-numDespacho",
    "2" : "Favor de escoger el CEDIS\n1. MONTERREY \n2. HERMOSILLO\n3. CANCUN\n4. COA",
    "3" : "Lo sentimos no tenemos asesor disponible"
}

_Data = {
    "1" :  "Porfavor ingresa tu numero de compra seguido del despacho\nEj. numCompra-numDespacho",
    "1.1" : {
        "123-123" : "PROVEEDOR\nORDEN DE COMPRA Y DESPACHO\nCODIGO Y DESCRIPCION\nCANTIDAD\nCANTIDAD RECIBIDA\nFECHA DE NECESIDAD\nFECHA PACTADA\nCOMPRADOR\nMARCA",
        "113-113" : "PROVEEDOR\nORDEN DE COMPRA Y DESPACHO\nCODIGO Y DESCRIPCION\nCANTIDAD\nCANTIDAD RECIBIDA\nFECHA DE NECESIDAD\nFECHA PACTADA\nCOMPRADOR\nMARCA",
        "100-100" : "PROVEEDOR\nORDEN DE COMPRA Y DESPACHO\nCODIGO Y DESCRIPCION\nCANTIDAD\nCANTIDAD RECIBIDA\nFECHA DE NECESIDAD\nFECHA PACTADA\nCOMPRADOR\nMARCA"
    },
    "2" : "Favor de escoger el CEDIS\n1. MONTERREY \n2. HERMOSILLO\n3. CANCUN\n4. COA",
    "2.1" : {
        "1" : "1-1",
        "2" : "2-2",
        "3" : "3-3",
        "4" : "4-4"
    }
}

_Error ={
    "1.1" : "Lo sentimos su orden no existe o esta mal escrita, puedes volver a ingresarla o escribre salir para regresar al menú principal",
    "2.1" : "El CEDIS elegido no existe vuelve a elegir \n1. MONTERREY \n2. HERMOSILLO\n3. CANCUN\n4. COA"
} 



class NewMessageObserver():
    
    driver = None
    _Ids = []
    _Level = {}

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
            print(keyWord+" "+id)
            response = ""

            if keyWord == "salir" :
                self._Ids.remove(id)
                del self._Level[id]

            # FIRST CONTACT #
            if id in self._Ids :
                
                # HAS LEVEL #

                level = self._Level.get(id,None)
                if level :

                    print(level)
                    # GET DATA #
                    data = _Data.get(level,None)

                    print("data -->",data)
                    
                    # SEND RESPONSE #
                    if isinstance(data, str) :
                        return data
                    else :

                        # EXIT #
                        if data.get(keyWord,False):
                            self._Ids.remove(id)
                            del self._Level[id]

                        return data.get(keyWord,_Error[level])

                else :
                     
                    # SEND MENU #
                    response = _Menu.get(keyWord,_Menu["001"])

                    # ADD OR UPDATE LEVEL #
                    if _Menu.get(keyWord,False) != False :
                        if keyWord == "1" :
                            self._Level[id] = "1.1"

                        if keyWord == "2" :
                            self._Level[id] = "2.1"
                        else : 
                            self._Level[id] = keyWord

                    print("Nivel --> ",self._Level)

            else : 
                self._Ids.append(id)
                response = _Menu["000"]

            # RETURN #
            return response
                 
        except Exception :
            logs.logError('Master-bot initSession',traceback.format_exc())
            return _Menu["001"]


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


