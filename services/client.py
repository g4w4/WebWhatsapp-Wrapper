#!/usr/bin/env python3
import os, sys, time, json
from socketIO_client_nexus import SocketIO, LoggingNamespace
# config files #
import config

# master path #
sys.path.insert(0,config.masterPath)

# system modules #
from Utils import logs
from models import master_hd


socketIO = SocketIO(config.ip,3000, LoggingNamespace)
masterClass = master_hd.start(socketIO)

##### SOCKET LISSENER #####
socketIO.on('connect', masterClass.on_connect)
socketIO.on('welcome', masterClass.on_welcome)
    # socketIO.on('reconnect', on_reconnect)
    # socketIO.on('getQr',on_getQr)
    # socketIO.on('matchUpdate',on_matchUpdate)
    # socketIO.on('giveScreen',on_giveScreen)
    # socketIO.on('sendText',on_sendText)
    # socketIO.on('sendFile',on_sendFile)
    # socketIO.on('deleteChat',on_deleteChat)

socketIO.wait()