cmake_minimum_required(VERSION 3.12)
project(driver_daemon)

set(CMAKE_CXX_STANDARD 17)

find_package(PkgConfig REQUIRED)
find_package(sdbus-c++ REQUIRED)
find_package(sdbus-c++-tools REQUIRED)
pkg_check_modules(SYSTEMD REQUIRED libsystemd)

# Use the sdbus-c++-xml2cpp in SDBusCpp namespace to generate the headers
add_custom_command(
  OUTPUT DriverServiceAdaptor.h DriverServiceProxy.h
  COMMAND
    SDBusCpp::sdbus-c++-xml2cpp
    ${PROJECT_SOURCE_DIR}/dbus/top.goosople.notouchscreen.DriverService.xml
    --adaptor=${PROJECT_SOURCE_DIR}/DriverServiceAdaptor.h
    --proxy=${PROJECT_SOURCE_DIR}/DriverServiceProxy.h
  DEPENDS dbus/top.goosople.notouchscreen.DriverService.xml
  COMMENT "Generating D-Bus interfaces for ${PROJECT_NAME}.")

add_executable(driver_daemon driver_daemon.cpp DriverServiceAdaptor.h
                             DriverServiceProxy.h)
target_link_libraries(driver_daemon PRIVATE SDBusCpp::sdbus-c++
                                            ${SYSTEMD_LIBRARIES})

install(TARGETS driver_daemon DESTINATION /usr/bin)
install(FILES driver_daemon.service DESTINATION /etc/systemd/system)
install(FILES dbus/top.goosople.notouchscreen.DriverService.xml
        DESTINATION /usr/share/dbus-1/interfaces)
install(FILES dbus/top.goosople.notouchscreen.conf
        DESTINATION /usr/share/dbus-1/system.d)
