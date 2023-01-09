from aqt import mw, gui_hooks
from aqt.utils import showInfo
from aqt.qt import *

import datetime

import sys
# check if system is windows
if sys.platform.startswith("win"):
    sys.path.append( os.path.join(os.getenv('APPDATA'), 'Anki2', 'addons21', 'neo-leaderboard'))


from anki_stats import get_review_count_today
from pocketbase_api import PB, User
import login
from consts import POCKETBASE_URL, ADDON_FOLDER

# dev
def log(msg):
    print(f"NAL: {msg}")

def log_review_count(show=False):
    log(f"Review count today: {get_review_count_today()}")

    if show:
        showInfo(f"Review count today: {get_review_count_today()}")
    
def on_load():
    # read user data from config
    config = mw.addonManager.getConfig(ADDON_FOLDER)
    
    if config and "user_data" in config:        
        user_data = config["user_data"]
        
        pb = PB(POCKETBASE_URL)
        pb.user = User(user_data, pb)
        
        mw.NAL_PB = pb
        
def on_anki_sync():
    r = get_review_count_today()
    
    try:
        mw.NAL_PB.user.set_reviews(datetime.datetime.now(), r)
        
        # showInfo(f"Synced review count to NAL: {r}")
    except Exception as e:
        showInfo(f"Error syncing review count to NAL: {e}")
        
        return
    
# ===========
# MAIN
# ===========

log("="*20)
log("Neo Anki leaderboard addon loaded")
log("="*20)

# setup hooks
gui_hooks.sync_did_finish.append(log_review_count)
gui_hooks.sync_did_finish.append(on_anki_sync)
gui_hooks.profile_did_open.append(on_load)

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
