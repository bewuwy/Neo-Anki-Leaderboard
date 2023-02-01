from aqt import mw
from aqt.qt import *

from consts import *


class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(f'About {APP_NAME}')
        self.setMinimumWidth(500)

        layout = QGridLayout()

        # title header
        label_title = QLabel(f'<font size="6"> {APP_NAME} </font>')
        layout.addWidget(label_title, 0, 0, 1, 2)
        
        # version
        label_version = QLabel(f'<font size="4"> Version: {VERSION} </font>')
        layout.addWidget(label_version, 1, 0, 1, 2)
        
        # made by
        label_author = QLabel(f'<font size="4"> Made by bewu</font>')
        layout.addWidget(label_author, 2, 0, 1, 2)

        # debug log
        label_log = QLabel('<font size="4"> Debug Log </font>')
        log_area = QTextEdit()
        log_area.setReadOnly(True)
        log_area.setText("\n".join(mw.NAL_LOG))
        layout.addWidget(label_log, 3, 0)
        layout.addWidget(log_area, 4, 0)
        
        copy_log_button = QPushButton('Copy Log')
        def copy_log():
            mw.app.clipboard().setText("\n".join(mw.NAL_LOG))
        qconnect(copy_log_button.clicked, copy_log)
        layout.addWidget(copy_log_button, 5, 0, 1, 2)

        # buttons
        button_close = QPushButton('Close')
        qconnect(button_close.clicked, self.close)
        layout.addWidget(button_close, 7, 0)
        
        layout.setRowMinimumHeight(5, 75)

        self.setLayout(layout)
