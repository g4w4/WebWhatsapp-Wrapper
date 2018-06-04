import os
import abc

from selenium.common.exceptions import WebDriverException
from six import string_types
from threading import Thread
from .objects.message import factory_message


class JsException(Exception):
    def __init__(self, message=None):
        super(Exception, self).__init__(message)


class WapiPhoneNotConnectedException(Exception):
    def __init__(self, message=None):
        super(Exception, self).__init__(message)


class WapiJsWrapper(object):
    """
    Wraps JS functions in window.WAPI for easier use from python
    """

    def __init__(self, driver, wapi_driver):
        self.driver = driver
        self.wapi_driver = wapi_driver

        # Starts new messages observable thread.
        self.new_messages_observable = NewMessagesObservable(self, wapi_driver, driver)
        self.new_messages_observable.start()

    def __getattr__(self, item):
        """
        Finds functions in window.WAPI

        :param item: Function name
        :return: Callable function object
        :rtype: JsFunction
        """
        wapi_functions = dir(self)

        if item not in wapi_functions:
            raise AttributeError("Function {0} doesn't exist".format(item))

        return JsFunction(item, self.driver)

    def __dir__(self):
        """
        Reloads wapi.js and returns its functions

        :return: List of functions in window.WAPI
        """
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()
        with open(os.path.join(script_path, "js", "wapi.js"), "r") as script:
            self.driver.execute_script(script.read())

        result = self.driver.execute_script("return window.WAPI")
        if result:
            return result.keys()
        else:
            return []


class JsArg(object):
    """
    Represents a JS function argument
    """

    def __init__(self, obj):
        """
        Constructor

        :param obj: Python object to represent
        """
        self.obj = obj

    def __str__(self):
        """
        Casts self.obj from python type to valid JS literal

        :return: JS literal represented in a string
        """
        if isinstance(self.obj, string_types):
            return repr(str(self.obj))

        if isinstance(self.obj, bool):
            return str(self.obj).lower()

        return str(self.obj)


class JsFunction(object):
    """
    Callable object represents functions in window.WAPI
    """

    def __init__(self, function_name, driver):
        self.driver = driver
        self.function_name = function_name

    def __call__(self, *args, **kwargs):
        # Selenium's execute_async_script passes a callback function that should be called when the JS operation is done
        # It is passed to the WAPI function using arguments[0]
        if len(args):
            command = "return WAPI.{0}({1}, arguments[0])" \
                .format(self.function_name, ",".join([str(JsArg(arg)) for arg in args]))
        else:
            command = "return WAPI.{0}(arguments[0])".format(self.function_name)

        try:
            self.driver.set_script_timeout(500)
            return self.driver.execute_async_script(command)
        except WebDriverException as e:
            if e.msg == 'Timed out':
                raise WapiPhoneNotConnectedException("Phone not connected to Internet")
            raise JsException("Error in function {0} ({1}). Command: {2}".format(self.function_name, e.msg, command))


class NewMessageObserver(metaclass=abc.ABCMeta):
    def __init__(self):
        pass

    @abc.abstractmethod
    def on_message_received(self, new_messages):
        return


class NewMessagesObservable(Thread):
    def __init__(self, wapi_js_wrapper, wapi_driver, webdriver):
        Thread.__init__(self)
        self.daemon = True
        self.wapi_js_wrapper = wapi_js_wrapper
        self.wapi_driver = wapi_driver
        self.webdriver = webdriver
        self.observers = []

    def run(self):
        while True:
            try:
                self.webdriver.set_script_timeout(115200)  # One hour timeout for this execution
                new_js_messages = self.wapi_js_wrapper.waitNewMessages(True)
                new_messages = []
                for js_message in new_js_messages:
                    new_messages.append(factory_message(js_message, self.wapi_driver))

                self._inform_all(new_messages)
            except WapiPhoneNotConnectedException as e:
                pass
            except Exception as e:
                pass

    def subscribe(self, observer):
        if str(type(observer)) != "<type 'NewMessageObserver'>":
            raise Exception('You need to inform an observable that extends \'NewMessageObserver\'.')

        self.observers.append(observer)

    def unsubscribe(self, observer):
        self.observers.remove(observer)

    def _inform_all(self, new_messages):
        for observer in self.observers:
            observer.on_message_received(new_messages)