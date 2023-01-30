from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo

from consts import *
import login

import anki_stats
from dev import log

def setup_menu():
    menu = None
    add_menu = False

    # remove old menu
    for i in mw.form.menubar.actions():
        if i.text() == "NeoLeaderBoard":
            menu = i.menu()
            menu.clear()
    
    if not menu:
        # create new menu
        menu = QMenu("NeoLeaderBoard", mw)
        add_menu = True
    
    # open leaderboard action
    open_lb_action = QAction("Open Leaderboard", mw)
    def open_lb():
        url = QUrl(LEADERBOARD_WEBSITE + '?ref=anki')
        QDesktopServices.openUrl(url)
    qconnect(open_lb_action.triggered, open_lb)
    menu.addAction(open_lb_action)

    if not mw.NAL_PB or not mw.NAL_PB.user:        
        # login action
        login_action = QAction("Login", mw)
        def show_login_dialog():
            mw.loginWidget = login.LoginDialog()
            mw.loginWidget.show()
        qconnect(login_action.triggered, show_login_dialog)
        menu.addAction(login_action)
        
        # register action
        register_action = QAction("Register", mw)
        def open_register():
            url = QUrl(LEADERBOARD_WEBSITE + 'register?ref=anki')
            QDesktopServices.openUrl(url)
        qconnect(register_action.triggered, open_register)
        menu.addAction(register_action)
    else:
        # show user info action
        show_profile_action = QAction("Show Profile", mw)
        def show_profile():
            url = QUrl(LEADERBOARD_WEBSITE + 'user/' + mw.NAL_PB.user.id + '?ref=anki')
            QDesktopServices.openUrl(url)
        qconnect(show_profile_action.triggered, show_profile)
        menu.addAction(show_profile_action)
        
        # logout action
        logout_action = QAction("Logout", mw)
        def logout():
            mw.NAL_PB.logout()
            mw.NAL_PB = None
            setup_menu()
        qconnect(logout_action.triggered, logout)
        menu.addAction(logout_action)

        # full sync action
        full_sync_action = QAction("Full Sync", mw)
        def full_sync():
            try:
                mw.NAL_PB.user.full_sync()
            except AttributeError as e:
                log(f"User not logged in and tried to full-sync")
            except Exception as e:
                log(f"Error full-syncing review count to NAL: {e}")
            else:
                showInfo("Full sync complete")

        qconnect(full_sync_action.triggered, full_sync)
        menu.addAction(full_sync_action)
    
    # debug action
    if DEV_MODE:
        debug_action = QAction("Debug", mw)
        def on_debug_action():
            log(anki_stats.get_time_spent())
        qconnect(debug_action.triggered, on_debug_action)
        menu.addAction(debug_action)

    if add_menu:
        # add the whole addon menu to the main menu
        mw.form.menubar.insertMenu(mw.form.menuTools.menuAction(), menu)
