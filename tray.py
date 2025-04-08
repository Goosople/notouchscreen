#!python3

import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction, QIcon


class TrayIcon(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        self.setIcon(QIcon.fromTheme("dialog-information"))

        self.menu = QMenu()

        action_quit = QAction("", self.menu)
        action_quit.triggered.connect(self.on_quit)
        self.menu.addAction(action_quit)

        self.setContextMenu(self.menu)

        self.activated.connect(self.on_tray_click)

    def on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            print("")  # switch touch screen

    def on_quit(self):
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    tray = TrayIcon()
    tray.show()
    sys.exit(app.exec())
