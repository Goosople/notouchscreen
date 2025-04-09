#!/usr/bin/env python3
import os
import sys
import dbus
from PyQt6.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QMenu,
    QMessageBox,
)
from PyQt6.QtGui import QAction, QIcon

DRIVER_PATH = os.getenv(
    "TOUCHSCREEN_DRIVER_PATH", "/sys/bus/hid/drivers/hid-multitouch"
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


def show_error(err):
    QMessageBox(
        QMessageBox.Icon.Critical,
        _("Error"),
        err,
        QMessageBox.StandardButton.Close,
    ).exec()


def get_devices():
    try:
        return list(
            filter(
                lambda f: os.path.isdir(os.path.join(DRIVER_PATH, f)) and ":" in f,
                os.listdir(DRIVER_PATH),
            )
        )
    except FileNotFoundError:
        show_error(_("DEVICE_PATH is not found"))
        QApplication.quit()
    except PermissionError:
        show_error(_("Permission denied to get devices"))
        QApplication.quit()
    except Exception as e:
        show_error(_("Unknown error") + f": {e}")
        QApplication.quit()


def switch_touchscreen(device):
    device["status"] = not device["status"]
    try:
        result = dbus.Interface(
            dbus.SystemBus().get_object(
                "top.goosople.notouchscreen.DriverService",
                "/top/goosople/notouchscreen/DriverService",
            ),
            "top.goosople.notouchscreen.DriverService",
        ).switchTouchscreen(device["id"], device["status"])
        print(result)
    except dbus.exceptions.DBusException as e:
        show_error(str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    device = {"id": get_devices()[0], "status": True}  # TODO: add selection
    tray = TrayIcon()
    tray.show()
    sys.exit(app.exec())
