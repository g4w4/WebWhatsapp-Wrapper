from interfaces import interface_messages
from threading import Thread

class NewMessageObserver():
    
    socket = None
    driver = None

    def __init__(self,socket,driver): 
        self.socket = socket
        self.driver = driver

    def on_message_received(self, new_messages):   
        for message in new_messages:
            if message.get('isGroup') :
                group = message._js_obj.get('chat').get('id').get('_serialized')
                me = "{}@c.us".format(driver.get_phone_number())
                exitGroup = Thread(target=driver.remove_participant_group,args=(group,me))
                exitGroup.start()
            else : 
                _message = interface_messages.getFormat(message,self.driver)
                self.socket.emit('newMessage',_message)