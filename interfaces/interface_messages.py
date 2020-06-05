from Utils import logs
import shutil
import traceback
import os
from services import config
import datetime,uuid


__DOCUMENT_TYPE = {
    'document' : 'document',
    'image' : 'image',
    'video' : 'video',
    'audio' : 'audio',
    'ptt' : 'ptt',
    'chat' : 'chat'
}

class IdMessage(): 
    _idMessage = None
    message = None

    def __init__(self,message):
        self.message = message
        self._idMessage = dict({"id":None,"sendBy":None})
    
    def get(self):
        _id = self.message.id.split("_")
        self._idMessage["id"] = _id[2]
        self._idMessage["sendBy"] = "Agent" if self.message._js_obj['sender']['isMe'] else "Client"
        return self._idMessage


class ContentMessage():
    __DOCUMENT_TYPE = {
        'document' : 'document',
        'image' : 'image',
        'video' : 'video',
        'audio' : 'audio',
        'ptt' : 'ptt',
        'chat' : 'chat'
    }
    content = None
    message = None

    def __init__(self,message):
        self.message = message
        self.content = dict({
            "content" : None,
            "type" : "txt",
            "caption" : "false"
        })

    """
    Retorna el contenido y el tipo de mensaje
    Returns {type,caption,content}
    """
    def get(self):

        if self.message.type not in self.__DOCUMENT_TYPE :
            # Media no soportada #
            self.content["content"] = 'No soportado'

        elif self.message.type != "chat" and self.message.type in self.__DOCUMENT_TYPE :
            # Guara el contenido del archivo #
            self.content["content"] = str( self.message.save_media(config.pathFiles,True) ).replace(config.pathFiles,"")
            newName =  uuid.uuid1().hex + self.content["content"]
            os.rename(config.pathFiles+self.content["content"],config.pathFiles+newName)
            self.content["content"] = newName

        else :
            # Obtiene el contenido del texto #
            self.content["content"] =  self.message.content
        
        # Si el mensaje es un archivo y esta dento de los soportados #
        if self.message.type in self.__DOCUMENT_TYPE and self.message.type != "chat" :

            # Guardamos su tipo y su descripción #
            self.content["type"] = self.message.type
            self.content["caption"] = self.message.caption

        return self.content


"""
Retorna el objeto del mensaje
Params (message) message
Returns { chat,sendBy,message,type,caption,akc,date,id,app }
"""
def getFormat(message,driver):
    try:
        _id = IdMessage(message).get()
        chat = message._js_obj.get('chat').get('id').get('_serialized')
        contentMessage = ContentMessage(message).get()   
        return {
            "chat": chat,
            "sendBy": _id["sendBy"],
            "message": contentMessage["content"],
            "type": contentMessage["type"],
            "caption": contentMessage["caption"],
            "akc": 2,
            "date": message.timestamp.strftime("%Y-%m-%d %H:%M"),
            "id": _id["id"],
            "app": "whatsApp"       
        }

    except Exception :
        logs.logError('Error getFormat --> ',traceback.format_exc())

"""
Retorna el objeto del mensaje de ubicación
Params (message) message
Returns { chat,sendBy,message,type,caption,lng,lat,akc,date,id,app }
"""
def getLocation(message,diver):
    _id = IdMessage(message).get()
    chat = message._js_obj.get('chat').get('id').get('_serialized')
    return {
        "chat": chat,
        "sendBy": _id["sendBy"],
        "message": "Ubicación",
        "type": "location",
        "caption": "false",
        "lng": message._js_obj['lng'],  
        "lat": message._js_obj['lat'],
        "akc": 2,
        "date": message.timestamp.strftime("%Y-%m-%d %H:%M"),
        "id": _id["id"],
        "app": "whatsApp"       
    }


def getFormatText(message,chatId):
    try:
        return {
            "chat": chatId,
            "sendBy": "Agent",
            "message": message,
            "type": "txt",
            "caption": "false",
            "akc": 1,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "id": uuid.uuid1().hex,
            "app": "whatsApp"       
        }
    except Exception :
        logs.logError('Error getFormatText --> ',traceback.format_exc())

def getFormatFile(message,chatId,typeFile,caption):

    try:
        return {
            "chat": chatId,
            "sendBy": "Agent",
            "message": message,
            "type": typeFile,
            "caption": caption,
            "akc": 1,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "id": uuid.uuid1().hex,
            "app": "whatsApp"       
        }
    except Exception :
        logs.logError('Error getFormatText --> ',traceback.format_exc())