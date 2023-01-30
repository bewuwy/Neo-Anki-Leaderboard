from aqt.qt import *

#* add addon folder to path
import sys, pathlib
addon_path = pathlib.Path(__file__).parent.resolve()
sys.path.append(str(addon_path))

from dev import log

#* ===========
#* MAIN
#* ===========

log("="*20, True)
log("Neo Anki leaderboard addon loaded", True)
log("="*20, True)

log(addon_path, True)

#* hooks
from hooks import setup_hooks
setup_hooks()
