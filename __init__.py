from aqt.qt import *
from aqt import mw

#* add addon folder to path
import sys, pathlib
addon_path = pathlib.Path(__file__).parent.resolve()
sys.path.append(str(addon_path))

from dev import log
from consts import *

#* ===========
#* MAIN
#* ===========

mw.NAL_LOG = []

log(f"{APP_NAME} addon loaded")
log(f"version: {VERSION}")
if DEV_MODE:
    log("debug mode")
log("folder: " + ADDON_FOLDER)

#* hooks
from hooks import setup_hooks
setup_hooks()
