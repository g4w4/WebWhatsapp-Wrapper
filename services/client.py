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


socketIO = SocketIO(config.ip,3005, LoggingNamespace)
masterClass = master_hd.start(socketIO)

##### SOCKET LISSENER #####
socketIO.on('connect', masterClass.on_connect)
socketIO.on('welcome', masterClass.on_welcome)
socketIO.on('reconnect', masterClass.on_reconnect)
socketIO.on('disconnect', masterClass.on_disconnect)
socketIO.on('getQr',masterClass.on_getQr)
socketIO.on('getScreen',masterClass.on_getScreen)
socketIO.on('sendTest',masterClass.on_test)
socketIO.on('sendText',masterClass.on_sendText)
socketIO.on('sendTextNewTicket',masterClass.on_sendTextNewTicket)
socketIO.on('sendFile',masterClass.on_sendFile)
socketIO.on('deleteChat',masterClass.on_deleteChat)
## PENDIENTES ###
socketIO.on('sendMessageGroup',masterClass.on_sendMessageGroup)
socketIO.on('validNumber',masterClass.on_isValid)
socketIO.on('blockNumber',masterClass.on_blockNumber)

socketIO.wait()