import os, sys, time, json
import config
from Utils import logs

class start():
    socketIO = None
    wsp = None
    driver = None
    awaitLogin = None

    def __init__(self,socket): 
        if not os.path.exists(config.pathSession): os.makedirs(config.pathSession)
        self.socketIO = socket

    def on_connect(self,*args):
        print(args)
        logs.logError('Socket-Info','Connection whit server')
        self.socketIO.emit('Auth',config.token)