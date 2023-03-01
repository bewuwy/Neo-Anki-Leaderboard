from aqt import mw, gui_hooks #, QThread
import datetime

from dev import log, info, error, popup
import anki_stats
from menu import setup_menu
from consts import *
from pocketbase_api import PB, UpdateLBError
from qt_workers import TokenRefresher #, LBSyncer


def on_load():
    # read user data from config
    # log("addon folder " + ADDON_FOLDER)
    
    config = mw.addonManager.getConfig(ADDON_FOLDER)
    
    if config and "user_data" in config:        
        user_data = config["user_data"]
        
        pb = PB(POCKETBASE_URL)
        pb.login_from_data(user_data)
        
        mw.nal_token_refresher = TokenRefresher(pb)
        mw.nal_token_refresher.start()
        
        mw.NAL_PB = pb
    else:
        mw.NAL_PB = None
    
    setup_menu()
    
    if mw.NAL_PB:
        # check for new medals
        medals_new = mw.NAL_PB.user.get_medals()
        medals_old = mw.addonManager.getConfig(ADDON_FOLDER).get("medals", [])
        
        if medals_new != medals_old:
            delta_medals = [m for m in medals_new if m not in medals_old]

            msg = "You've earned a new medal!"
            if len(delta_medals) > 1:
                msg = "You've earned new medals!"
            
            for m in delta_medals:
                msg += f"\n{m['place'].capitalize()} in {m['date']} for {m['type']}"
            
            msg += "\n\nCheck it out on the website!"
            
            info(msg)
            
            config = mw.addonManager.getConfig(ADDON_FOLDER)
            config["medals"] = medals_new
            mw.addonManager.writeConfig(ADDON_FOLDER, config)

def on_anki_sync():
    # mw.lb_sync_thread = QThread()
    # syncer = LBSyncer(mw.NAL_PB)
    # syncer.moveToThread(mw.lb_sync_thread)
    # mw.lb_sync_thread.started.connect(syncer.run)
    # syncer.finished.connect(mw.lb_sync_thread.quit)
    # syncer.finished.connect(syncer.deleteLater)
    # mw.lb_sync_thread.finished.connect(mw.lb_sync_thread.deleteLater)
    
    # mw.lb_sync_thread.start()
    # # delete thread after it's finished
    # # mw.lb_sync_thread.finished.connect(lambda: delattr(mw, "lb_sync_thread"))
    
    r = anki_stats.get_review_count()
            
    try:
        mw.NAL_PB.user.set_reviews(datetime.datetime.utcnow(), r)
        
        log(f"Syncing review count to NAL: {r}")
    except AttributeError:
        info("User not logged in and tried to sync")
    except UpdateLBError:
        popup("Couldn't update leaderboard. Try logging out and back in.")
    except Exception as e:
        info(f"Error syncing review count to NAL. See log for details")
        error()    
    
def setup_hooks():
    gui_hooks.sync_did_finish.append(on_anki_sync)
    gui_hooks.profile_did_open.append(on_load)
