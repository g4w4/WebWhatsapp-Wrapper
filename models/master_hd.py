import os, sys, time, json
import shutil
import traceback
from uuid import uuid4
from threading import Thread
from webwhatsapi import WhatsAPIDriver
from webwhatsapi.objects.message import Message, MediaMessage
import config
from Utils import logs, telegram
from models import _wapi,observable
from interfaces import interface_events
import concurrent.futures


class start():
    socketIO = None
    wsp = None
    driver = None
    awaitLogin = None
    __Keyword = "Master-Info"
    sessionStart = False
    messagesStore = {}


    def __init__(self,socket): 
        if not os.path.exists(config.pathSession): os.makedirs(config.pathSession)
        self.socketIO = socket

    """  Cacha la conección exitosa al server y manda la auth """
    def on_connect(self,*args):
        logs.logError('Socket-Info','Connection whit server')
        event = interface_events.auth(config.token)
        telegram.telegram("Conectado al server")
        self.socketIO.emit( event["event"], event["info"] )  

    """ Realiza la negociación para el inicio de sessión en whatsApp 
        Params args[0] token de autentificación
    """
    def on_welcome(self,*args):
        logs.logError('Socket-Info','welcome to server {}'.format(args[0]))
        telegram.telegram("Inicio de sessión")
        self.__AUTH = args[0]
        try:

            # Valida si existe sessión previa en el webSocket o no #
            logs.logError('on_welcome','Connection success')
            if self.driver != None and self.driver.is_logged_in():
                
                # Se envían los datos de la sessión #
                telegram.telegram("Reconección exitosa")
                general_info = _wapi.getGeneralInfo(self.driver)
                event = interface_events.send_status(self.__AUTH, general_info["whatsAppJoin"], general_info["numero"] )
                self.socketIO.emit( event["event"], event["info"] )

                if( self.driver.is_connected() ) :
                    logs.logError('on_welcome','inician los hilos')
                    telegram.telegram("Inicio de sessión exitoso -->")
                    self.startThreads( self.messagesStore, self.socketIO )
                
            else:
                # Envia que esta desconectado de whatsApp#
                event = interface_events.send_status(self.__AUTH)
                self.socketIO.emit( event["event"], event["info"] )

                # Intenta conectar a whatsApp #
                logs.logError('on_welcome','Revisando si hay sessión')
                event = interface_events.send_alert(self.__AUTH, "'Revisando si hay sessión")
                self.socketIO.emit( event["event"], event["info"] )
                self.driver = WhatsAPIDriver(profile=config.pathSession, client='remote', command_executor=config.selemiunIP)
                rember = _wapi.rememberSession(self.driver,self.socketIO)

                if rember :

                    # Se envían los datos de la sessión #
                    telegram.telegram("Conecctando a WA")
                    general_info = _wapi.getGeneralInfo(self.driver)
                    event = interface_events.send_status(self.__AUTH, general_info["whatsAppJoin"], general_info["numero"] )
                    self.socketIO.emit( event["event"], event["info"] )

                    # Inician los hilos #
                    logs.logError('on_welcome','Session recordada inician los hilos')
                    telegram.telegram("Inicio de sessión exitoso")
                    self.startThreads( self.messagesStore, self.socketIO )

                else :

                    # No hay sesión es necesarío el login por qr #
                    logs.logError('on_welcome','Sesión olvidada, necesarío QR')
                    telegram.telegram("Session olvidada necesarío QR")
                    event = interface_events.send_alert(self.__AUTH, "Sessión olvidada")
                    self.socketIO.emit( event["event"], event["info"] )

        except Exception :
            telegram.telegram("Welcome-Error {} ".format(traceback.format_exc()))
            logs.logError('Welcome-Error',traceback.format_exc())
            # Envia que esta desconectado de whatsApp#
            event = interface_events.send_status(self.__AUTH)
            self.socketIO.emit( event["event"], event["info"] )

            # Envia alerta #
            event = interface_events.send_alert(self.__AUTH, "Error requiere reinicio")
            self.socketIO.emit( event["event"], event["info"] )

    """ Cacha el evento de desconección y manda el log """
    def on_disconnect(self,*args):
        telegram.telegram("Desconectado del server")
        logs.logError('on_disconnect','Connection end')
        os.exit(0)

    """ Cacha el evento de reconección y emite la auth """
    def on_reconnect(self,*args):
        telegram.telegram("Desconectado del server")
        logs.logError('on_disconnect','Connection end')
        os.exit(0)
        event = interface_events.auth(config.token)
        telegram.telegram("Conectado al server")
        self.socketIO.emit( event["event"], event["info"] )  

    """ Cacha la petición de qr 
        Params args[0] socket_id ID del receptor
    """
    def on_getQr(self,*args):
        socket_id = args[0]
        try:
            logs.logError('on_getQr','Solicitando QR')
            if self.driver == None :
                self.driver = WhatsAPIDriver(profile=config.pathSession, client='remote', command_executor=config.selemiunIP)

            # Pedimos el qr #
            name = _wapi.getQrCode(self.driver)
            logs.logError('on_getQr','Enviando QR')

            # Enviamos el resultado #
            event = interface_events.send_qr(self.__AUTH,socket_id,name)
            self.socketIO.emit( event["event"], event["info"] )

            try:
                # Iniciamos el proceso de login #
                logs.logError('on_getQr', 'Esprando login')
                session = _wapi.waitLogin(self.driver, self.socketIO)

                if session:

                    logs.logError('on_getQr', 'Login exitoso')
                    event = interface_events.send_login_status(self.__AUTH,socket_id,"Sessión iniciada", 200)
                    self.socketIO.emit( event["event"], event["info"] )

                    # Iniciamos observable #
                    logs.logError('on_getQr', 'Iniciando hilos')
                    self.startThreads( self.messagesStore, self.socketIO )
                   
                    # Enviamos los generales de la cuenta #
                    general_info = _wapi.getGeneralInfo(self.driver)
                    event = interface_events.send_status(self.__AUTH, general_info["whatsAppJoin"], general_info["numero"] )
                    self.socketIO.emit( event["event"], event["info"] )

                    # Enviamos el resultado del login #
                    event = interface_events.send_status(self.__AUTH, general_info["whatsAppJoin"], general_info["numero"] )
                    self.socketIO.emit( event["event"], event["info"] )
                    
                else:
                    logs.logError('on_getQr', 'Se acabo el tiempo')
                    event = interface_events.send_login_status(self.__AUTH,socket_id,"Se acabo el timpo reintente reiniciando", 500)
                    self.socketIO.emit( event["event"], event["info"] )
                    # ALERT #
            except Exception :
                logs.logError('on_getQr',traceback.format_exc())
                # Enviamos el Error #
                event = interface_events.send_login_status(self.__AUTH,socket_id,"Error iniciando sessión revise logs", 500)
                self.socketIO.emit( event["event"], event["info"] )

        except Exception :
            logs.logError('on_getQr',traceback.format_exc())
            # Enviamos el Error #
            event = interface_events.send_qr_error(self.__AUTH,socket_id,"Error solicitando QR reinicie la cuenta")
            self.socketIO.emit( event["event"], event["info"] )

    """ Cacha la petición de obtener el screen 
        Parmas args[0] socket_id ID del receptor
    """
    def on_getScreen(self,*args):
        socket_id = args[0]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(_wapi.getScreen, self.driver)
            result = future.result(timeout=30)
            if result["code"] == 200:
                event = interface_events.send_screen(self.__AUTH,socket_id,result["name"])
                self.socketIO.emit( event["event"], event["info"] )
            else:
                event = interface_events.send_screen_error(self.__AUTH,socket_id,result["name"])
                self.socketIO.emit( event["event"], event["info"] )
    
    """ Envía un mensaje de texto al numero ingresado
        Parmas args[0] number Numero a 10 digitos
        Parmas args[1] message Mensaje a enviar
        Parmas args[2] socket_id Id del receptor
    """
    def on_test(self,*args):
        try:
            number= args[0] 
            message= args[1]
            socket_id= args[2]  
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future= executor.submit(_wapi.send_test, self.driver, number, message)
                result= future.result(timeout=120)
                message_result= "Test exitoso" if result["code"] == 200 else result["error"]

                event = interface_events.send_test_result(self.__AUTH,socket_id,message_result)
                self.socketIO.emit( event["event"], event["info"] )
        except Exception :
            telegram.telegram("Error NO ENVIA {} ".format(traceback.format_exc()))

    """ Envía un mensaje de texto a un cliente
        Parmas args[0] message Mensaje a enviar
        Parmas args[1] id_chat Id del chat
        Parmas args[2] message_id Id del mensaje
    """
    def on_sendText(self,*args):
        try:
            print(args)
            message = args[0]
            id_chat = args[1]
            message_id = args[2]
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future= executor.submit(_wapi.send_text, self.driver,id_chat,message)
                result= future.result(timeout=120)
                akc= 2 if result["code"] == 200 else 0
                event = interface_events.send_message_status(self.__AUTH,message_id,akc)
                self.socketIO.emit( event["event"], event["info"] )
        except Exception :
            telegram.telegram("Error NO ENVIA {} ".format(traceback.format_exc()))

    def on_sendTextNewTicket(self,*args):
        try:
            print(args)
            message = args[0]
            id_chat = args[1]
            message_id = args[2]
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future= executor.submit(_wapi.send_text_new_tt, self.driver,id_chat,message)
                result= future.result(timeout=120)
                akc= 2 if result["code"] == 200 else 0
                event = interface_events.send_message_status(self.__AUTH,message_id,akc)
                self.socketIO.emit( event["event"], event["info"] )
        except Exception :
            telegram.telegram("Error NO ENVIA {} ".format(traceback.format_exc()))

    def on_sendMessageGroup(self,*args):
        send = Thread(target=_wapi.sendText,args=(self.driver,self.socketIO,config.groupId,'I am here'))
        send.start()

    """ Envia un mensaje con archivo
        Parmas args[0] message Mensaje a enviar
        Parmas args[1] caption Mensaje a enviar
        Parmas args[2] id_chat Id del chat
        Parmas args[3] message_id Id del mensaje
    """
    def on_sendFile(self,*args):
        try:
            message = args[0]
            caption = args[1]
            id_chat = args[2]
            message_id = args[3]
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future= executor.submit(_wapi.send_file,self.driver,id_chat,caption,message)
                result= future.result(timeout=120)
                print(result)
                akc= 2 if result["code"] == 200 else 0
                event = interface_events.send_message_status(self.__AUTH,message_id,akc)
                self.socketIO.emit( event["event"], event["info"] )
        except Exception :
            telegram.telegram("Error NO ENVIA {} ".format(traceback.format_exc()))

    """ Borra el chat del teléfono para liberar memoria
        Parmas args[0] id_chat Id del chat
    """
    def on_deleteChat(self,*args):
        return
        # id_chat = args[0]
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     future= executor.submit(_wapi.deleteChat,self.driver,id_chat)
        #     result= future.result(timeout=30)
        #    print(result)

    """ Inicia el observable para recibir los mensajes """
    def startThreads(self,*args):
        try:
            logs.logError('startThreads','Pregunatmos si se inicia')
            if self.sessionStart == False:
                logs.logError('startThreads','Si, si se inicia')

                # Envia todos los mensajes recibidos
                _wapi.getOldMessages( self.driver, self.socketIO, self.__AUTH)

                self.sessionStart = True
                self.driver.subscribe_new_messages(observable.NewMessageObserver(self.socketIO,self.driver, self.__AUTH))

                # Inicia el pool #
                loop = Thread(target=self.poolConnection,args=())
                loop.start()

            else:
                logs.logError('startThreads','No, no se inicia')
        except Exception:
            logs.logError('startThreads',traceback.format_exc())

    """ Mantiene vivo el socket """
    def poolConnection(self):
        try:
            #while True:
            time.sleep(60)
            general_info = _wapi.getGeneralInfo(self.driver)
            event = interface_events.send_status(self.__AUTH, general_info["whatsAppJoin"], general_info["numero"] )
            self.socketIO.emit( event["event"], event["info"] )

            while True:
                time.sleep(60)
                is_connected = self.driver.is_connected()
                if is_connected == False:
                    telegram.telegram("Cuenta sin RED")

        except  Exception :
            telegram.telegram("Welcome-Error {} ".format(traceback.format_exc()))

    def sincGetOldMessages(self,*args):
        chats = _wapi.getOldMessages(self.driver,args[0],args[1])
        self.socketIO.emit('oldMessages',chats)

    def on_isValid(self,*args):
        id = args[0][0]
        valid = Thread(target=_wapi.isValid,args=(self.driver,self.socketIO,id))
        valid.start()

    def on_blockNumber(self,*args):
        id = args[0][0]
        print('Bloqueo de numero'+ id)
        valid = Thread(target=_wapi.blockNumber,args=(self.driver,self.socketIO,id))
        valid.start()

        
        
