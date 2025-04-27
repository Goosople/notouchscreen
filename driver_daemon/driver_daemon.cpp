#include "DriverServiceAdaptor.h"
#include <csignal>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sdbus-c++/IConnection.h>
#include <sdbus-c++/Types.h>
#include <sdbus-c++/sdbus-c++.h>
#include <string>
#include <systemd/sd-daemon.h>
#include <thread>
#include <unistd.h>
#include <vector>

using namespace top::goosople::notouchscreen;
namespace fs = std::filesystem;

const fs::path DRIVER_PATH = "/sys/bus/hid/drivers/hid-multitouch";
const fs::path DEVICE_PATH = "/sys/bus/hid/devices";

class Driver final {
private:
    Driver() = default;

    std::fstream bindFile;

public:
    static Driver& getInstance()
    {
        static Driver inst;
        return inst;
    }

    Driver(const Driver&) = delete;
    Driver& operator=(const Driver&) = delete;

    ~Driver() = default;

    bool isValidDevice(std::string device_id)
    {
        return fs::is_directory(DEVICE_PATH / device_id);
    }

    bool setTouchscreen(std::string device_id, bool status)
    {
        if (!isValidDevice(device_id))
            return false;
        if (bindFile.is_open())
            bindFile.close();
        bindFile.open(DRIVER_PATH / (status ? "bind" : "unbind"));
        bindFile << device_id;
        bool result = bindFile.good();
        bindFile.close();
        return result;
    }
};

class DriverService : public sdbus::AdaptorInterfaces<DriverService_adaptor> {
public:
    DriverService(sdbus::IConnection& connection, sdbus::ObjectPath path)
        : AdaptorInterfaces(connection, std::move(path))
    {
        registerAdaptor();
    }

    ~DriverService() { unregisterAdaptor(); }

private:
    bool switchTouchscreen(const std::string& device_id, const bool& status)
    {
        return Driver::getInstance().setTouchscreen(device_id, status);
    }
};

int main()
{
    auto connection = sdbus::createSystemBusConnection(
        sdbus::ServiceName("top.goosople.notouchscreen.DriverService"));

    DriverService service(
        *connection,
        sdbus::ObjectPath("/top/goosople/notouchscreen/DriverService"));
    sd_notify(0, "READY=1");

    connection->enterEventLoop();

    return 0;
}
