from aqt import mw, gui_hooks
import datetime

from menu import setup_menu
import anki_stats
from consts import *
from pocketbase_api import PB

from dev import log


def on_load():
    # read user data from config
    # log("addon folder " + ADDON_FOLDER)
    
    config = mw.addonManager.getConfig(ADDON_FOLDER)
    
    if config and "user_data" in config:        
        user_data = config["user_data"]
        
        pb = PB(POCKETBASE_URL)
        pb.login_from_data(user_data)
        
        mw.NAL_PB = pb
    else:
        mw.NAL_PB = None
    
    setup_menu()

def on_anki_sync():
    r = anki_stats.get_review_count()
    
    try:
        mw.NAL_PB.user.set_reviews(datetime.datetime.now(), r)
        
        # showInfo(f"Synced review count to NAL: {r}")
        log(f"Synced review count to NAL: {r}", True)
    except AttributeError:
        # showInfo("You need to login first")
        log("User not logged in and tried to sync")
    except Exception as e:
        log(f"Error syncing review count to NAL: {e}")
        
        return
    
def setup_hooks():
    gui_hooks.sync_did_finish.append(on_anki_sync)
    gui_hooks.profile_did_open.append(on_load)