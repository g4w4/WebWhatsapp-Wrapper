#!/usr/bin/env python3
import os, sys, time, json
from socketIO_client_nexus import SocketIO, LoggingNamespace
# config files #
from services import config

# master path #
sys.path.insert(0,config.masterPath)

# system modules #
from Utils import logs


class start():
    socketIO = None
    wsp = None
    driver = None
    awaitLogin = None

    def __init__(self,socket,driver): 
        if not os.path.exists(config.pathSession): os.makedirs(config.pathSession)
        self.socketIO = SocketIO(config.ip,3000, LoggingNamespace)

    def on_connect(*args):
        logs.logError('Socket-Info','Connection whit server')
        self.socketIO.emit('Auth',"token")

    ##### SOCKET LISSENER #####
    socketIO.on('connect', on_connect)
    # socketIO.on('welcome', on_welcome)
    # socketIO.on('reconnect', on_reconnect)
    # socketIO.on('getQr',on_getQr)
    # socketIO.on('matchUpdate',on_matchUpdate)
    # socketIO.on('giveScreen',on_giveScreen)
    # socketIO.on('sendText',on_sendText)
    # socketIO.on('sendFile',on_sendFile)
    # socketIO.on('deleteChat',on_deleteChat)

    socketIO.wait()


start()