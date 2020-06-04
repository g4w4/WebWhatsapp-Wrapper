from interfaces import interface_messages
from threading import Thread
from Utils import logs, telegram
import config
import traceback
from interfaces import interface_events

class NewMessageObserver():
    
    socket = None
    driver = None

    """ Inicializa el servicio 
    Params socket(socketIO)
    Params driver(selenumWarper)
    Params token(str) Token de auth
    """
    def __init__(self,socket,driver, token): 
        self.socket = socket
        self.driver = driver
        self.token = token
        self.socket.on('welcome',self.update_token)

    """
    Recibira si fue actualizado el token
    Params args[0] token
    """
    def update_token(self,*args):
        print("Recibio ")
        print( args[0] )
        self.token = args[0]


    """
    Recibe el objeto del mensaje
    Params: new_messages (Array<message>)
    """
    def on_message_received(self, new_messages):
        logs.write_log('Muevo mensaje de --> es llamado ')
        for message in new_messages:
            logs.write_log('Muevo mensaje de -->',message._js_obj.get('chat').get('id'))
            try:

                # Valida si el mensaje es de un grupo #
                group = message._js_obj.get('chat').get('id').get('_serialized')
                if self.driver.is_chat_group(group) :

                    # Si el grupo pertenece al grupo de auth lo manda #
                    if group == config.groupId:
                        # Emite de quien recibio el mensaje # 
                        self.socket.emit('getStatusAccount', message._js_obj['author'].get('_serialized') )
                else :

                    if  message._js_obj['type'] == "location":

                        # Si es una ubicación #
                        _message = interface_messages.getLocation( message, self.driver)
                        event = interface_events.new_message_ubication(self.token, _message)
                        self.socket.emit( event["event"], event["info"] )
                    else:

                        # Si es media o texto #
                        _message = interface_messages.getFormat(message,self.driver)
                        event = interface_events.new_message(self.token, _message)
                        self.socket.emit( event["event"], event["info"] )
            except Exception :
                telegram.telegram("Error observable {}".format(traceback.format_exc()))
                print(traceback.format_exc())