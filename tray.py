#!/usr/bin/env python3
import os
import sys
from PyQt6.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QMenu,
    QMessageBox,
)
from PyQt6.QtGui import QAction, QIcon

DEVICE_PATH = os.getenv(
    "NOTOUCHSCREEN_DEVICE_PATH", "/sys/bus/hid/drivers/hid-multitouch"
)

global device


def _(s):
    return s  # TODO: a placeholder for future localization


class TrayIcon(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        self.setIcon(QIcon.fromTheme("dialog-information"))

        self.menu = QMenu()

        action_quit = QAction("Quit", self.menu)
        action_quit.triggered.connect(self.on_quit)
        self.menu.addAction(action_quit)

        self.setContextMenu(self.menu)

        self.activated.connect(self.on_tray_click)

    def on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            switch_touchscreen(device)

    def on_quit(self):
        QApplication.quit()


def show_error_and_exit(err):
    QMessageBox(
        QMessageBox.Icon.Critical,
        _("Error"),
        err,
        QMessageBox.StandardButton.Close,
    ).exec()
    QApplication.quit()


def get_devices():
    try:
        return list(
            filter(
                lambda f: os.path.isdir(os.path.join(DEVICE_PATH, f)) and ":" in f,
                os.listdir(DEVICE_PATH),
            )
        )
    except FileNotFoundError:
        show_error_and_exit(_("DEVICE_PATH is not found"))
    except PermissionError:
        show_error_and_exit(_("Permission denied to get devices"))
    except Exception as e:
        show_error_and_exit(_("Unknown error") + f": {e}")


def switch_touchscreen(device):
    print(device)
    return  # FIXME: implement


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    device = get_devices()[0]  # TODO: add selection
    tray = TrayIcon()
    tray.show()
    sys.exit(app.exec())
