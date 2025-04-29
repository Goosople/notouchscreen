# NoTouchScreen

一个用于通过系统托盘启用/禁用触摸屏功能的Linux工具。

## 功能

- 单击即可开关触摸屏
- 系统托盘集成，方便访问
- 自动检测触摸屏设备
- 支持多个触摸屏设备
- 退出时恢复触摸屏功能

## 要求

- 带有systemd的Linux系统
- Python 3.x和PyQt6
- D-Bus
- libsystemd
- sdbus-c++

## 安装

### 构建驱动守护程序

```bash
cd driver_daemon
mkdir build && cd build
cmake ..
make
sudo make install
```

### 启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable driver_daemon
sudo systemctl start driver_daemon
```

### 运行托盘应用程序

```bash
python3 tray.py
```

要在登录时自动启动，请将`tray.py`添加到您的桌面环境的启动应用程序中。

## 使用方法

- **左键点击**托盘图标以开关触摸屏功能
- **右键点击**访问菜单：
    - **更改设备**：选择其他触摸屏设备
    - **退出**：退出应用程序（触摸屏将被重新启用）

## 工作原理

NoTouchScreen由两个主要组件组成：

1. **系统托盘应用程序**（Python/PyQt6）：提供用户界面并与驱动守护程序通信。

2. **驱动守护程序**（C++）：以提升的权限运行，通过sysfs修改触摸屏驱动状态。

这些组件之间的通信通过D-Bus处理，提供安全的特权操作，而无需GUI应用程序以root身份运行。

## 从源码构建

### 前提条件

```bash
# 对于守护程序
sudo apt install cmake libsystemd-dev libsdbus-c++-dev pkg-config

# 对于托盘应用程序
pip install PyQt6 dbus-python
```

然后按照上述安装说明进行操作。

## 许可证

![GPLv3或更高版本标志](https://www.gnu.org/graphics/gplv3-or-later.svg)

此项目采用GNU通用公共许可证第3版或更高版本授权 - 详见[LICENSE](LICENSE)文件。