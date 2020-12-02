from interfaces import interface_messages
from threading import Thread
from Utils import logs
import config
import traceback

class NewMessageObserver():
    
    socket = None
    driver = None

    def __init__(self,socket,driver): 
        self.socket = socket
        self.driver = driver

    def on_message_received(self, new_messages):
        logs.write_log('NewMessage 2 FROM -->',new_messages)
        for message in new_messages:
            logs.write_log('NewMessage FROM -->',message._js_obj.get('chat').get('id'))
            try:
                group = message._js_obj.get('chat').get('id').get('_serialized')
                if self.driver.is_chat_group(group) :
                    if group == config.groupId:
                        print( "GRUPO" )
                        print( message._js_obj['author'].get('_serialized') )
                        self.socket.emit('getStatusAccount', message._js_obj['author'].get('_serialized') )
                    else:
                        print( "GRUPO" )
                        me = "{}@c.us".format(self.driver.get_phone_number())
                        # exitGroup = Thread(target=self.driver.remove_participant_group,args=(group,me))
                        # exitGroup.start()
                else :
                    if  message._js_obj['type'] == "location":
                        print( "Es ubicación" )
                        print(  message._js_obj['lng']  )
                        print(  message._js_obj['lat']  )
                        _message = interface_messages.getLocation( message, self.driver)
                        self.socket.emit('newMessage',_message)
                    else:
                        print( "Es Nomarl" )
                        _message = interface_messages.getFormat(message,self.driver)
                        print(_message)
                        self.socket.emit('newMessage',_message)
            except Exception :
                print(traceback.format_exc())