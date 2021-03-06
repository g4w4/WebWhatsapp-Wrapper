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

    def get(self):

        if self.message.type not in self.__DOCUMENT_TYPE :
            # MEDIA NOT SUPORTED #
            self.content["content"] = 'Contenido no soportado'

        elif self.message.type != "chat" and self.message.type in self.__DOCUMENT_TYPE :
            # SAVE MEDIA #
            self.content["content"] = str( self.message.save_media(config.pathFiles,True) ).replace(config.pathFiles,"")
            print("1---->"+self.content["content"] )
            newName =  uuid.uuid1().hex + self.content["content"]
            os.rename(config.pathFiles+self.content["content"],config.pathFiles+newName)
            self.content["content"] = newName
            print("2---->"+self.content["content"] )

        else :
            # GET TEXT #
            self.content["content"] =  self.message.content
        
        if self.message.type in self.__DOCUMENT_TYPE and self.message.type != "chat" :
            # GET TYPE AND CAPTION#
            self.content["type"] = self.message.type
            self.content["caption"] = self.message.caption

        return self.content


####################### getFormat(message,driver) ###################
# Desc : Give format to message                                      #
# Params : message objWapi driver obj                                #       
# Return :  obj {chat,sendBy,messsage,type,caption}                  #                          
# Last Update : 30-05-19                                             #
# By : g4w4                                                          #
######################################################################
def getFormat(message,driver):
    try:
        _id = IdMessage(message).get()
        chat = message._js_obj.get('chat').get('id').get('_serialized')
        chat = '521{}'.format(str(chat)[-15:len(str(chat))])
        contentMessage = ContentMessage(message).get()   
        return {
            "chat": chat,
            "sendBy": _id["sendBy"],
            "message": contentMessage["content"],
            "type": contentMessage["type"],
            "caption": contentMessage["caption"],
            "akc": 1,
            "date": message.timestamp.strftime("%Y-%m-%d %H:%M"),
            "id": _id["id"],
            "app": "whatsApp"       
        }

    except Exception :
        logs.logError('Error getFormat --> ',traceback.format_exc())

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

def getLocation(message,diver):
    _id = IdMessage(message).get()
    chat = message._js_obj.get('chat').get('id').get('_serialized')
    chat = '521{}'.format(str(chat)[-15:len(str(chat))])
    return {
        "chat": chat,
        "sendBy": _id["sendBy"],
        "message": "Ubicación",
        "type": "location",
        "caption": "false",
        "lng": message._js_obj['lng'],  
        "lat": message._js_obj['lat'],
        "akc": 1,
        "date": message.timestamp.strftime("%Y-%m-%d %H:%M"),
        "id": _id["id"],
        "app": "whatsApp"       
    }

