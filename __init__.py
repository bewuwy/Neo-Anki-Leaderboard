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

log("="*20)
log(f"{APP_NAME} addon loaded")
log("="*20)

log("addon folder: " + ADDON_FOLDER)

#* hooks
from hooks import setup_hooks
setup_hooks()
