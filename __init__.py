from aqt import mw, gui_hooks
from aqt.utils import showInfo
from aqt.qt import *

import sys
# check if system is windows
if sys.platform.startswith("win"):
    sys.path.append( os.path.join(os.getenv('APPDATA'), 'Anki2', 'addons21', 'neo-leaderboard'))

from anki_stats import get_review_count_today
import login

# dev
def log(msg):
    print(f"NAL: {msg}")

def log_review_count(show=False):
    log(f"Review count today: {get_review_count_today()}")

    if show:
        showInfo(f"Review count today: {get_review_count_today()}")

# ===========
# MAIN
# ===========

log("="*20)
log("Neo Anki leaderboard addon loaded")
log("="*20)

# setup hooks
gui_hooks.sync_did_finish.append(log_review_count)

# setup menu
menu = QMenu("LeaderBoard", mw)

# test action
testAction = QAction("test", mw)
def testFunction():
    log_review_count(True)
qconnect(testAction.triggered, testFunction)
menu.addAction(testAction)

# login action
login_action = QAction("Login", mw)
def show_login_dialog():
    mw.loginWidget = login.LoginDialog()
    mw.loginWidget.show()
qconnect(login_action.triggered, show_login_dialog)
menu.addAction(login_action)

# add the whole addon menu to the main menu
mw.form.menubar.insertMenu(mw.form.menuTools.menuAction(), menu)
