from interfaces import interface_messages

class NewMessageObserver():
    
    socket = None
    driver = None

    def __init__(self,socket,driver): 
        self.socket = socket
        self.driver = driver

    def on_message_received(self, new_messages):
        for message in new_messages:
            _message = interface_messages.getFormat(message,self.driver)
            self.socket.emit('newMessage',_message)