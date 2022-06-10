from configparser import ConfigParser
from PyQt5.QtWidgets import (
    QApplication, QWidget,
    QGridLayout, QLabel,
    QLineEdit, QVBoxLayout,
    QHBoxLayout, QPushButton
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal

try:
    from src.constants import *
    from src.linkssettings import LinksSettings
except:
    import sys, os
    sys.path.insert(0, os.path.dirname(sys.path[0]))
    from constants import *
    from linkssettings import LinksSettings
    import rc.resources

class Settings(QWidget):

    apply_settings = pyqtSignal()

    def __init__(self, parser, parent=None):
        super(Settings, self).__init__(parent)
        self.parser = parser
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setup_UI()
        self.destroyed.connect(Settings._on_destroyed)

    @staticmethod
    def _on_destroyed():
        print("Settings instance deleted.")

    def setup_UI(self):
        self.setWindowIcon(QIcon(":/gear_icon.png"))
        self.setWindowTitle("Settings")
        self.mainlayout = QVBoxLayout()
        self.inputslayout = QGridLayout()
        self.btnslayout = QHBoxLayout()
        self.setup_inputs()
        self.setup_btns()
        self.setLayout(self.mainlayout)
        self.resize(self.mainlayout.sizeHint())
        self.setMinimumWidth(640)

    def setup_inputs(self):
        self.inputs_conf = {
            "app_title": ("App Title:", QLineEdit),
            "header_title": ("Header Title:", QLineEdit),
            "email": ("Email:", QLineEdit),
        }
        self.inputs = {}
        row = 0
        col = 0
        for name, val in self.inputs_conf.items():
            obj = None
            col = 0
            label = QLabel(val[0])
            col += 1
            if val[1] == QLineEdit:
                obj = val[1]()
            self.inputslayout.addWidget(label, row, col)
            col += 1
            self.inputslayout.addWidget(obj, row, col)
            self.inputs[name] = (label, obj)
            row += 1
        self.mainlayout.addLayout(self.inputslayout)

        self.inputs["app_title"][1].setText(self.parser.get("application", "title"))
        self.inputs["header_title"][1].setText(self.parser.get("application", "header_title"))
        self.inputs["email"][1].setText(self.parser.get("mail", "email"))

    def setup_btns(self):
        self.btns_conf = {
            "cancel": ("Cancel", self.close),
            "submit": ("Apply", self.apply)
        }
        self.btns = {}
        self.btns["links"] = QPushButton("URL Links")
        self.btns["links"].clicked.connect(self.open_links_settings)
        self.btnslayout.addWidget(self.btns["links"])
        self.btnslayout.addStretch()
        for name, val in self.btns_conf.items():
            btn = QPushButton(val[0])
            btn.clicked.connect(val[1])
            self.btnslayout.addWidget(btn)
            self.btns[name] = btn

        self.mainlayout.addLayout(self.btnslayout)

    def apply(self):
        self.parser.set("application", "title", self.inputs["app_title"][1].text())
        self.parser.set("application", "header_title", self.inputs["header_title"][1].text())
        self.parser.set("mail", "email", self.inputs["email"][1].text())
        with open(APP_CONFIG, "w") as cfgfile:
            self.parser.write(cfgfile)
        self.apply_settings.emit()
        self.close()

    def keyPressEvent(self, key_event):
        if key_event.key() == Qt.Key.Key_Return:
            self.apply()
        elif key_event.key() == Qt.Key.Key_Escape:
            self.close()
        return super().keyPressEvent(key_event)

    def open_links_settings(self):
        self.linkssettings = LinksSettings(self.parser)
        self.linkssettings.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.linkssettings.show()

if __name__=="__main__":
    parser = ConfigParser()
    parser.read(APP_CONFIG)
    app = QApplication(sys.argv)
    widget = Settings(parser)
    widget.show()
    sys.exit(app.exec())