from aqt import mw
from aqt.utils import showInfo
import datetime
import traceback

from consts import *

def log(msg):
    mw.NAL_LOG.append(f'{datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}: {msg}')
    
    print(f"NAL: {msg}")

def popup(msg):
    info(str(msg), force_show=True)

def info(msg, force_print=False, force_show=False):
    if (DEV_MODE and not force_print) or force_show:
        showInfo(str(msg), title=APP_NAME)
    
    log(msg)
    
def error():
    msg = traceback.format_exc()
    log(msg)
