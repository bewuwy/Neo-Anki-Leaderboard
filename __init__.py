from aqt import mw, gui_hooks
from aqt.utils import showInfo
from aqt.qt import *

from pocketbase import PocketBase
import datetime


def log(msg):
    print(f"NAL: {msg}")


log("="*20)
log("Anki leaderboard addon loaded")
log("="*20)


def get_review_count_today():
    start_date = datetime.datetime.today()
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    end_date = datetime.datetime.today() + datetime.timedelta(days=1)

    start = int(start_date.timestamp() * 1000)
    end = int(end_date.timestamp() * 1000)

    reviews = mw.col.db.scalar(
        "SELECT COUNT(*) FROM revlog WHERE id >= ? AND id < ? AND ease > 0", start, end)

    return reviews


def log_review_count(show=False):
    log(f"Review count today: {get_review_count_today()}")

    if show:
        showInfo(f"Review count today: {get_review_count_today()}")


gui_hooks.sync_did_finish.append(log_review_count)

# create a new menu
menu = QMenu("Leaderboard", mw)
# create a new menu item
action = QAction("test", mw)
# set it to call testFunction when it's clicked


def testFunction():
    log_review_count(True)


qconnect(action.triggered, testFunction)
# and add it to the menu
menu.addAction(action)


class LoginDialog(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('LeaderBoard Login')
        self.resize(500, 120)

        layout = QGridLayout()

        label_name = QLabel('<font size="4"> Username </font>')
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText('Please enter your username')
        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.lineEdit_username, 0, 1)

        label_password = QLabel('<font size="4"> Password </font>')
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setPlaceholderText('Please enter your password')
        self.lineEdit_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(label_password, 1, 0)
        layout.addWidget(self.lineEdit_password, 1, 1)

        button_login = QPushButton('Login')
        qconnect(button_login.clicked, self.login_user)
        layout.addWidget(button_login, 2, 0, 1, 2)
        layout.setRowMinimumHeight(2, 75)

        self.setLayout(layout)

    def login_user(self):
        log("login_user")
        
        user = self.lineEdit_username.text()
        password = self.lineEdit_password.text()
        
        msg = QMessageBox()
        msg.setText(f"Login failed {user}/{password}")
        
        pb = PocketBase("https://pb-anki-lb.fly.dev/")

        try:
            user_data = pb.users.auth_via_email(user, password)
        except:
            user_data = None

        if user_data:
            msg.setText(f"{user_data}")
        
        msg.exec_()


def show_login_dialog():
    log("show_login_dialog")

    mw.loginWidget = LoginDialog()
    mw.loginWidget.show()


login_action = QAction("Login", mw)
menu.addAction(login_action)
qconnect(login_action.triggered, show_login_dialog)


# and add the whole menu to the main menu
mw.form.menubar.insertMenu(mw.form.menuTools.menuAction(), menu)
