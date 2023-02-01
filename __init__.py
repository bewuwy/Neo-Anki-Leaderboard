from aqt.qt import *
from aqt import mw

#* add addon folder to path
import sys, pathlib
addon_path = pathlib.Path(__file__).parent.resolve()
sys.path.append(str(addon_path))

from dev import info
from consts import *

#* ===========
#* MAIN
#* ===========

mw.NAL_LOG = []

info("="*20, True)
info(f"{APP_NAME} addon loaded", True)
info("="*20, True)

info(ADDON_FOLDER, True)

#* hooks
from hooks import setup_hooks
setup_hooks()
