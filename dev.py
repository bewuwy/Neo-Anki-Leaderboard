from aqt.utils import showInfo

from consts import DEV_MODE


def log(msg, force_print=False):
    if DEV_MODE and not force_print:
        showInfo(str(msg))
    
    print(f"NAL: {msg}")
