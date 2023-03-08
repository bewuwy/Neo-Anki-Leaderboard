from aqt import mw
from aqt.qt import *

from consts import *
import login, about

import anki_stats
from pocketbase_api import UpdateLBError
import xp_system
from dev import info, error, popup

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
        url = QUrl(LEADERBOARD_WEBSITE + 'board/week?ref=anki')
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
                info(f"User not logged in and tried to full-sync")
            except UpdateLBError:
                info("Couldn't update leaderboard. Try logging out and back in.")
            except Exception as e:
                info(f"Error full-syncing review count to NAL. See log for details.")
                error()
            else:
                popup("Full sync complete")

        qconnect(full_sync_action.triggered, full_sync)
        menu.addAction(full_sync_action)
    
    # bug report action
    issue_action = QAction("Report a Bug", mw)
    def on_issue_action():
        log_short = []
        for line in mw.NAL_LOG:
            # remove up to first ": "
            line = line[line.find(": ")+2:]

            log_short.append(line)
        
        issue_body = f"Describe your issue:\n\nDebug log:\n```\n{'%0A'.join(log_short)}\n```"
        url = QUrl(GITHUB_URL + f"issues/new?labels=bug&body={issue_body}")
        QDesktopServices.openUrl(url)
    qconnect(issue_action.triggered, on_issue_action)
    menu.addAction(issue_action)
    
    # about action
    about_action = QAction("About", mw)
    def on_about_action():
        mw.aboutWidget = about.AboutWindow()
        mw.aboutWidget.show()
    qconnect(about_action.triggered, on_about_action)
    menu.addAction(about_action)
    
    # debug action
    if DEV_MODE:
        debug_action = QAction("Debug", mw)
        def on_debug_action():
            today_reviews, today_retention = anki_stats.get_review_count_retention()
            
            xp = xp_system.calc_xp(today_reviews, today_retention)
            
            popup(f"Today's reviews: {today_reviews}\nToday's retention: {today_retention}\nXP: {xp}")
        
        qconnect(debug_action.triggered, on_debug_action)
        menu.addAction(debug_action)

    if add_menu:
        # add the whole addon menu to the main menu
        mw.form.menubar.insertMenu(mw.form.menuTools.menuAction(), menu)
