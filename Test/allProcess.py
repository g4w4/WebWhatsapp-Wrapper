from Utils.logs import write_log
import os, sys, time, json
import shutil
import traceback
from webwhatsapi import WhatsAPIDriver
from webwhatsapi.objects.message import Message, MediaMessage
import shutil
from uuid import uuid4
from threading import Thread

print("Start v2.0.0")