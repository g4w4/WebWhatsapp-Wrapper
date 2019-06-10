#!/usr/bin/env python3
import os, sys, time, json
from flask import Flask, send_from_directory, request, Response
import traceback

# config files #
import configAPI

sys.path.insert(0,configAPI.masterPath)

from models import master_api
from Utils import logs

app = Flask(__name__)
master = master_api.start()

@app.route('/')
def hello_word():
	return json.dumps({"code":200,"desc":"Success"})


@app.route("/getQr",methods=["GET"])
def getQr():
    try:
        qr = master.getQr()
        if isinstance(qr,dict):
            return Response(json.dumps(qr), mimetype='application/json')
        else : 
            return send_from_directory(configAPI.pathFiles,qr)
    except Exception:
        logs.logError('Master-API',traceback.format_exc())
        return Response(json.dumps(master_api._Responses["500"]), mimetype='application/json')

@app.route("/getScreen",methods=["GET"])
def getScreen():
    try:
        screen = master.getScreen()
        if isinstance(screen,dict) :
            return Response(json.dumps(screen), mimetype='application/json')
        else : 
            return send_from_directory(configAPI.pathFiles,"{}.png".format(screen))
    except Exception:
        logs.logError('Master-API',traceback.format_exc())
        return Response(json.dumps(master_api._Responses["500"]), mimetype='application/json')

@app.route("/getChatList",methods=["POST"])
def getChatList():
    try:
        chatList = master.getChatList()
        return Response(json.dumps(chatList), mimetype='application/json')
    except Exception:
        logs.logError('Master-API',traceback.format_exc())
        return Response(json.dumps(master_api._Responses["500"]), mimetype='application/json')

@app.route("/sendMessage",methods=["POST"])
def sendMessage():
    try:
        message = master.sendMessage(request.form["idChat"],request.form["message"])
        print(message)
        return Response(json.dumps(message), mimetype='application/json')
    except Exception:
        logs.logError('Master-API',traceback.format_exc())
        return Response(json.dumps(master_api._Responses["500"]), mimetype='application/json')

@app.route("/isValid",methods=["POST"])
def isValid():
    try:
        valid = master.isValid(request.form["number"])
        return Response(json.dumps(valid), mimetype='application/json')
    except Exception:
        logs.logError('Master-API',traceback.format_exc())
        return Response(json.dumps(master_api._Responses["500"]), mimetype='application/json')
    

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0',port=configAPI.port)  