from aqt import mw, gui_hooks
from aqt.utils import showInfo
from aqt.qt import *

import datetime

import sys, pathlib, os
addon_path = pathlib.Path(__file__).parent.resolve()
sys.path.append(str(addon_path))

from anki_stats import get_review_count_today
from pocketbase_api import PB, User
import login
from consts import POCKETBASE_URL, ADDON_FOLDER, LEADERBOARD_WEBSITE

# ===========
# dev functions
# ===========

def log(msg):
    print(f"NAL: {msg}")

# ===========
# HOOKS
# ===========
    
def on_load():
    # read user data from config
    log("addon folder " + ADDON_FOLDER)
    
    config = mw.addonManager.getConfig(ADDON_FOLDER)
    
    if config and "user_data" in config:        
        user_data = config["user_data"]
        
        pb = PB(POCKETBASE_URL)
        pb.login_from_data(user_data)
        
        mw.NAL_PB = pb
        
def on_anki_sync():
    r = get_review_count_today()
    
    try:
        mw.NAL_PB.user.set_reviews(datetime.datetime.now(), r)
        
        # showInfo(f"Synced review count to NAL: {r}")
        log(f"Synced review count to NAL: {r}")
    except AttributeError:
        # showInfo("You need to login first")
        log("User not logged in and tried to sync")
    except Exception as e:
        showInfo(f"Error syncing review count to NAL: {e}")
        
        return
    
# ===========
# MAIN
# ===========

log("="*20)
log("Neo Anki leaderboard addon loaded")
log("="*20)

log(os.path.basename(addon_path))
log(addon_path)

# setup hooks
gui_hooks.sync_did_finish.append(on_anki_sync)
gui_hooks.profile_did_open.append(on_load)

# setup menu
menu = QMenu("LeaderBoard", mw)

# login action
login_action = QAction("Login", mw)
def show_login_dialog():
    mw.loginWidget = login.LoginDialog()
    mw.loginWidget.show()
qconnect(login_action.triggered, show_login_dialog)
menu.addAction(login_action)

# open leaderboard action
open_lb_action = QAction("Open Leaderboard", mw)
def open_lb():
    url = QUrl(LEADERBOARD_WEBSITE)
    QDesktopServices.openUrl(url)
qconnect(open_lb_action.triggered, open_lb)
menu.addAction(open_lb_action)

# add the whole addon menu to the main menu
mw.form.menubar.insertMenu(mw.form.menuTools.menuAction(), menu)
