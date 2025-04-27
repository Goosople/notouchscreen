#!/usr/bin/env python3
import os
import sys
import dbus
from PyQt6.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QMenu,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
)
from PyQt6.QtGui import QAction, QIcon

DRIVER_PATH = "/sys/bus/hid/drivers/hid-multitouch"
DEVICE_PATH = "/sys/bus/hid/devices"

global device, tray


def _(s):
    return s  # TODO: a placeholder for future localization


class TrayIcon(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        self.setIcon(QIcon("touch_enabled.svg"))
        # TODO: different icons for different status

        self.menu = QMenu()

        action_quit = QAction(_("Quit"), self.menu)
        action_quit.triggered.connect(self.on_quit)
        self.menu.addAction(action_quit)

        action_change_device = QAction(_("Change device"), self.menu)
        action_change_device.triggered.connect(self.on_change_device)
        self.menu.addAction(action_change_device)

        self.setContextMenu(self.menu)

        self.activated.connect(self.on_tray_click)

    def on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            switch_touchscreen(device)

    def on_change_device(self):
        global device
        device["id"] = select_device(False) or device["id"]

    def on_quit(self):
        QApplication.quit()


class ListOptionDialog(QDialog):
    def __init__(self, title, question, options, is_cancelable=True, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(question))

        self.list_widget = QListWidget()
        for option in options:
            item = QListWidgetItem(option)
            self.list_widget.addItem(item)

        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.list_widget)

        if options:
            self.list_widget.setCurrentRow(0)

        self.button_box = (
            QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok
                | QDialogButtonBox.StandardButton.Cancel
            )
            if is_cancelable
            else QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def selected_option(self):
        return self.list_widget.currentRow()


def show_error(err):
    QMessageBox.critical(
        None,
        _("Error"),
        err,
        buttons=QMessageBox.StandardButton.Close,
    )


def select_device(is_first_time=True):
    devices = get_devices()
    dialog = ListOptionDialog(
        _("Devices"),
        _("Select the device to control:"),
        devices,
        is_cancelable=not is_first_time,
    )
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return devices[dialog.selected_option()]
    else:
        return None


def is_touchscreen(device_id):
    driver = os.path.join(DEVICE_PATH, device_id, "driver")
    return (
        False
        if not os.path.islink(driver)
        else ("hid-multitouch" in os.path.realpath(driver))
    )


def get_devices():
    try:
        return list(filter(is_touchscreen, os.listdir(DEVICE_PATH)))
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
    tray.setIcon(
        QIcon("touch_enabled.svg" if device["status"] else "touch_disabled.svg")
    )
    try:
        dbus.Interface(
            dbus.SystemBus().get_object(
                "top.goosople.notouchscreen.DriverService",
                "/top/goosople/notouchscreen/DriverService",
            ),
            "top.goosople.notouchscreen.DriverService",
        ).switchTouchscreen(device["id"], device["status"])
    except dbus.exceptions.DBusException as e:
        show_error(str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    device = {"id": select_device(True) or get_devices()[0], "status": True}
    tray = TrayIcon()
    tray.show()
    sys.exit(app.exec())
