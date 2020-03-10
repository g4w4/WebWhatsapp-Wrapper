from services import config

"""
Retorna la información estruturada para los eventos del web socket

Returns: { event: (str), data: (object) }
"""

"""
Autentificación
Params: token (str) Token de inicio de sessión
Returns:  { event: (str), data: { token: (token) } }
"""
def auth(token):
    return {
        "event": "event",
        "info": {
            "event": "Auth",
            "info":{
                "token": token
            }
        }
    }

"""
Envia el estatus de la cuenta
Params: token(str) Token de auth
        whatsApp(str) "false" o "true"
        number(str) Opcional
"""
def send_status(token,whatsApp="false",number="false",status="Conectado al websocket"):
    return {
        "event": "event",
        "info": {
            "event": "sendStatusAccount",
            "info": {
                "token": token,
                "whatsApp": whatsApp,
                "number": number,
                "status": status
            }
        }
    }

"""
Envia alertas al server
Params: token(str) Token de auth
        message(str) Alerta enviada
"""
def send_alert(token,message):
    return {
        "event": "event",
        "info": {
            "event": "alertAccount",
            "info": {
                "token": token,
                "message": message
            }
        }
    }


"""
Envia el qr solicitado
Params: token(str) Token de auth
        socket_id(str) Id del receptor
        url(str) Url de la imagen
"""
def send_qr(token,socket_id,url):
    return {
        "event": "event",
        "info": {
            "event": "sendQr",
            "info": {
                "token": token,
                "socket_id": socket_id,
                "url": url
            }
        }
    }

"""
Envia si hay un error en qr solicitado
Params: token(str) Token de auth
        socket_id(str) Id del receptor
        message(str) Mensaje de error
"""
def send_qr_error(token,socket_id,message):
    return {
        "event": "event",
        "info": {
            "event": "sendQrError",
            "info": {
                "token": token,
                "socket_id": socket_id,
                "message": message
            }
        }
    }

"""
Envia si hay un error en el proceso de login
Params: token(str) Token de auth
        socket_id(str) Id del receptor
        message(str) Mensaje de error
        code(int) 200 o 500
"""
def send_login_status(token,socket_id,message,code):
    return {
        "event": "event",
        "info": {
            "event": "loginStatus",
            "info": {
                "token": token,
                "socket_id": socket_id,
                "message": message,
                "code":code
            }
        }
    }

"""
Envia el evento resultado del la petición del screen
Params: token(str) Token de auth
        socket_id(str) Id del receptor
        url(str) Url de la imagen
"""
def send_screen(token,socket_id,url):
    return {
        "event": "event",
        "info": {
            "event": "getScreenResult",
            "info": {
                "token": token,
                "socket_id": socket_id,
                "url":url
            }
        }
    }

"""
Envia el error en la petición del screen
Params: token(str) Token de auth
        socket_id(str) Id del receptor
        message(str) Mensaje del error
"""
def send_screen_error(token,socket_id,message):
    return {
        "event": "event",
        "info": {
            "event": "sendScreenError",
            "info": {
                "token": token,
                "socket_id": socket_id,
                "message":message
            }
        }
    }


"""
Envia el resultado del test de mensaje
Params: token(str) Token de auth
        socket_id(str) Id del receptor
        message(str) Mensaje
"""
def send_test_result (token,socket_id,message):
    return {
        "event": "event",
        "info": {
            "event": "testResult",
            "info": {
                "token": token,
                "socket_id": socket_id,
                "message":message
            }
        }
    }

"""
Envia el mensaje que ha recibido
Params: token(str) Token de auth
        message( chat,sendBy,message,type,caption,,akc,date,id,app ) Mensaje recibido
"""
def new_message( token, message):
    return {
        "event": "event",
        "info": {
            "event": "newMessage",
            "info": {
                "token": token,
                "message": {
                    "chat": message["chat"],
                    "sendBy": message["sendBy"],
                    "message":message["message"], 
                    "type": message["type"],
                    "caption": message["caption"],
                    "akc": message["akc"],
                    "date": message["date"],
                    "id": message["id"],
                    "app": message["app"],
                    "token_account": config.token
                }
            }
        }
    }

"""
Envia el mensaje de ubicación que ha recibido
Params: token(str) Token de auth
        message( chat,sendBy,message,type,caption,lng,lat,akc,date,id,app ) Mensaje recibido
"""
def new_message_ubication( token, message):
    return {
        "event": "event",
        "info": {
            "event": "newMessageUbication",
            "info": {
                "token": token,
                "message": {
                    "chat": message["chat"],
                    "sendBy": message["sendBy"],
                    "message":message["message"], 
                    "type": message["type"],
                    "caption": message["caption"],
                    "lng": message["lng"],
                    "lat": message["lat"],
                    "akc": message["akc"],
                    "date": message["date"],
                    "id": message["id"],
                    "app": message["app"],
                    "token_account": config.token
                }
            }
        }
    }


"""
Envia el mensaje que ha recibido
Params: token(str) Token de auth
        message( chat,sendBy,message,type,caption,,akc,date,id,app ) Mensaje recibido
"""
def new_message_old( token, message):
    return {
        "event": "event",
        "info": {
            "event": "newMessageOld",
            "info": {
                "token": token,
                "message": {
                    "chat": message["chat"],
                    "sendBy": message["sendBy"],
                    "message":message["message"], 
                    "type": message["type"],
                    "caption": message["caption"],
                    "akc": message["akc"],
                    "date": message["date"],
                    "id": message["id"],
                    "app": message["app"],
                    "token_account": config.token
                }
            }
        }
    }

"""
Envia el mensaje de ubicación que ha recibido
Params: token(str) Token de auth
        message( chat,sendBy,message,type,caption,lng,lat,akc,date,id,app ) Mensaje recibido
"""
def new_message_ubication_old( token, message):
    return {
        "event": "event",
        "info": {
            "event": "newMessageUbicationOld",
            "info": {
                "token": token,
                "message": {
                    "chat": message["chat"],
                    "sendBy": message["sendBy"],
                    "message":message["message"], 
                    "type": message["type"],
                    "caption": message["caption"],
                    "lng": message["lng"],
                    "lat": message["lat"],
                    "akc": message["akc"],
                    "date": message["date"],
                    "id": message["id"],
                    "app": message["app"],
                    "token_account": config.token
                }
            }
        }
    }


"""
Envia el estatus del envío del mensaje
Params: token(str) Token de auth
       message_id(int) Id del mensaje
       akc(int) Status del mensaje 0 = fallido 2 = enviado
"""
def send_message_status( token, message_id, akc):
    return {
        "event": "event",
        "info": {
            "event": "messageTextStatus",
            "info": {
                "token": token,
                "message_id": message_id,
                "akc": akc
            }
        }
    }

