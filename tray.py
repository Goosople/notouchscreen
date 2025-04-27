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


def _(s):
    """Placeholder for future localization."""
    return s


class TrayIcon(QSystemTrayIcon):
    def __init__(self, device):
        super().__init__()
        self.device = device
        self.setIcon(QIcon("touch_enabled.svg"))

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
            switch_touchscreen(self.device)
            self.setIcon(
                QIcon("touch_enabled.svg" if device["status"] else "touch_disabled.svg")
            )

    def on_change_device(self):
        self.device["id"] = select_device(False) or self.device["id"]

    def on_quit(self):
        QApplication.quit()


class ListOptionDialog(QDialog):
    def __init__(self, title, question, options, is_cancelable=True, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(question))

        self.list_widget = QListWidget()
        self.list_widget.addItems(options)
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
    """Show error message dialog."""
    QMessageBox.critical(
        None,
        _("Error"),
        err,
        buttons=QMessageBox.StandardButton.Close,
    )


def select_device(is_first_time=True):
    """Show device selection dialog."""
    devices = get_devices()
    if not devices:  # Handle empty device list
        show_error(_("No devices found"))
        return None

    dialog = ListOptionDialog(
        _("Devices"),
        _("Select the device to control:"),
        devices,
        is_cancelable=not is_first_time,
    )
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return devices[dialog.selected_option()]
    return None


def is_touchscreen(device_id):
    """Check if device is (possibly) a touchscreen."""
    driver = os.path.join(DEVICE_PATH, device_id, "driver")
    return (not os.path.exists(driver)) or (
        "hid-multitouch" in os.path.realpath(driver)
    )


def get_devices():
    """Get list of available touchscreen devices."""
    try:
        return [d for d in os.listdir(DEVICE_PATH) if is_touchscreen(d)]
    except FileNotFoundError:
        show_error(_("DEVICE_PATH is not found"))
    except PermissionError:
        show_error(_("Permission denied to get devices"))
    except Exception as e:
        show_error(_("Unknown error") + f": {e}")
    QApplication.quit()


def switch_touchscreen(device):
    """Toggle touchscreen status."""
    device["status"] = not device["status"]

    try:
        bus = dbus.SystemBus()
        proxy = bus.get_object(
            "top.goosople.notouchscreen.DriverService",
            "/top/goosople/notouchscreen/DriverService",
        )
        interface = dbus.Interface(
            proxy,
            "top.goosople.notouchscreen.DriverService",
        )
        interface.switchTouchscreen(device["id"], device["status"])
    except dbus.exceptions.DBusException as e:
        show_error(_("Daemon error") + f": {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Initialize device and tray without globals
    device = {"id": select_device(True), "status": True}
    if not device["id"]:  # Fallback if no selection
        devices = get_devices()
        device["id"] = devices[0] if devices else None

    tray = TrayIcon(device)  # Pass device reference
    tray.show()

    sys.exit(app.exec())
