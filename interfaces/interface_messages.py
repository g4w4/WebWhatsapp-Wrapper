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
    _idMessage = dict({"id":None,"sendBy":None})
    message = None

    def __init__(self,message):
        self.message = message
    
    def get(self):
        _id = self.message.id.split("_")
        self._idMessage["id"] = _id[2]
        self._idMessage["sendBy"] = "Agent" if _id[0] == "false" else "Client"
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
    content = dict({
        "content" : None,
        "type" : "txt",
        "caption" : "false"
    })
    message = None

    def __init__(self,message):
        self.message = message

    def get(self):
        if self.message.type not in self.__DOCUMENT_TYPE :
            # MEDIA NOT SUPORTED #
            self.content.content = 'No soportado'

        elif self.message.type != "chat" and self.message.type in self.__DOCUMENT_TYPE :
            # SAVE MEDIA #
            self.content["content"] = str( self.message.save_media(config.pathFiles,True) )

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

