from Utils import logs
import shutil
import traceback
import os
from configPath import pathFiles

__DOCUMENT_TYPE = {
    'document' : 'document',
    'image' : 'image',
    'video' : 'video',
    'audio' : 'audio',
    'ptt' : 'ptt',
    'chat' : 'chat'
}

####################### getFormat(message,driver) ###################
# Desc : Give format to message                                      #
# Params : message objWapi driver obj                                #       
# Return :  obj {chat,sendBy,messsage,type,caption}                  #                          #
# Last Update : 30-05-19                                             #
# By : g4w4                                                          #
######################################################################
def getFormat(message,driver):
    try:
        body = {
            'chat': message._js_obj.get('chat').get('id').get('_serialized'),
            'sendBy': True if driver.get_phone_number() == message.sender.id else False,
            'message' : str(message.save_media(pathFiles,True)) if message.type != "chat" else message.content,
            'type' : message.type if message.type != 'document' else False,
            'caption' : message.caption if message.type != "chat" else False
        }

        if message.type == 'document':
            body['type'] = 'file'
        elif message.type == 'audio' or message.type == 'ptt':
            content =  str(message.save_media(pathFiles,True))
            os.rename(content, content+'.ogg')
            body['message'] = content
            body['type'] = 'ogg'
        elif message.type not in __DOCUMENT_TYPE :
            body['message'] = 'No soportado'
            logs.logError('_messages --> not suported',message)

        return body

    except Exception :
        logs.logError('_messages --> getMessage',traceback.format_exc())
        return False
