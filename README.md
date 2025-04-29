# NoTouchScreen

A Linux utility to enable/disable touchscreen functionality via the system tray.

## Features

- Toggle touchscreen functionality with a single click
- System tray integration for easy access
- Auto-detection of touchscreen devices
- Supports multiple touchscreen devices
- Restores touchscreen functionality on exit

## Requirements

- Linux system with systemd
- Python 3.x with PyQt6
- D-Bus
- libsystemd
- sdbus-c++

## Installation

### Build the Driver Daemon

```bash
cd driver_daemon
mkdir build && cd build
cmake ..
make
sudo make install
```

### Start the Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable driver_daemon
sudo systemctl start driver_daemon
```

### Run the Tray Application

```bash
python3 tray.py
```

To start automatically on login, add `tray.py` to your desktop environment's startup applications.

## Usage

- **Left-click** on the tray icon to toggle touchscreen functionality on/off
- **Right-click** to access the menu:
    - **Change device**: Select a different touchscreen device
    - **Quit**: Exit the application (touchscreen will be re-enabled)

## How It Works

NoTouchScreen consists of two main components:

1. **System Tray Application** (Python/PyQt6): Provides the user interface and communicates with the driver daemon.

2. **Driver Daemon** (C++): Runs with elevated privileges to modify the touchscreen driver state via sysfs.

Communication between these components is handled via D-Bus, providing secure privileged operations without requiring the GUI application to run as root.

## Building from Source

### Prerequisites

```bash
# For the daemon
sudo apt install cmake libsystemd-dev libsdbus-c++-dev pkg-config

# For the tray application
pip install PyQt6 dbus-python
```

Then follow the installation instructions above.

## License

![GPLv3 or later logo](https://www.gnu.org/graphics/gplv3-or-later.svg)

This project is licensed under the GNU General Public License v3 or later - see the [LICENSE](LICENSE) file for details.