from aqt.qt import *
from dev import log

import sys, pathlib
addon_path = pathlib.Path(__file__).parent.resolve()
sys.path.append(str(addon_path))

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
