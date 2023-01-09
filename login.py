from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
from aqt.operations import QueryOp


from pocketbase_api import PB
from consts import POCKETBASE_URL


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
        qconnect(button_login.clicked, self.on_login_user)
        layout.addWidget(button_login, 2, 0, 1, 2)
        layout.setRowMinimumHeight(2, 75)

        self.setLayout(layout)

    def on_login_user(self):        
        user = self.lineEdit_username.text()
        password = self.lineEdit_password.text()
        
        op = QueryOp(
            parent=mw,
            op=login_user(user, password),
            success=on_login_success,
        )

        # if with_progress() is not called, no progress window will be shown.
        op.run_in_background()

def login_user(user, password) -> None:        
    pb = PB(POCKETBASE_URL)

    try:
        pb.login(user, password)
        user = pb.user
    except:
        user = None
        
    if user is None:
        showInfo("Login failed")
        return on_login_success
    
    showInfo(user.token)
    
    mw.NAL_PB = pb
    
    return on_login_success

def on_login_success(result) -> None:
    # showInfo("Login success")
    pass
