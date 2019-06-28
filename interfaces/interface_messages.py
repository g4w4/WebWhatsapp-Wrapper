from Utils import logs
import shutil
import traceback
import os
from services import config

__DOCUMENT_TYPE = {
    'document' : 'document',
    'image' : 'image',
    'video' : 'video',
    'audio' : 'audio',
    'ptt' : 'ptt',
    'chat' : 'chat'
}

def getId(message):
    _id = message.id

    return {
        "id" : _id.split("_")[2],
        "sendBy" : 'Agent' if _id.split("_")[0] == 'false' else 'Client'  
    }


def getMessageContent(message):
    content = {
        "content" : "",
        "type" : "txt",
        "caption" : False
    }

    if message.type not in __DOCUMENT_TYPE :
        # MEDIA NOT SUPORTED #
        content.content = 'No soportado'

    elif message.type != "chat" and message.type in __DOCUMENT_TYPE :
        # SAVE MEDIA #
        content.content = str(message.save_media(config.pathFiles,True))

    else :
        # GET TEXT #
        content.content =  message.content
    
    if message.type in __DOCUMENT_TYPE and message.type != "chat" :
        # GET TYPE AND CAPTION#
        content.type = message.type
        content.caption = message.caption

    return content


####################### getFormat(message,driver) ###################
# Desc : Give format to message                                      #
# Params : message objWapi driver obj                                #       
# Return :  obj {chat,sendBy,messsage,type,caption}                  #                          
# Last Update : 30-05-19                                             #
# By : g4w4                                                          #
######################################################################
def getFormat(message,driver):
    body = {}
    try:
        _id = getId(message)
        print(_id)
        chat = message._js_obj.get('chat').get('id').get('_serialized')
        contentMessage = getMessageContent(message)    
        print(contentMessage)
        
        return {
            "id" : _id.id,
            "message" : {
                "chat": chat,
                "sendBy": _id.sendBy,
                "message": contentMessage.content,
                "type": contentMessage.type,
                "caption": contentMessage.caption,
                "akc" : 1,
                "date" : message.timestamp       
            }
        }

    except Exception :
        logs.logError('Error interface message --> ',traceback.format_exc())

