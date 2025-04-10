#include "DriverServiceAdaptor.h"
#include <csignal>
#include <cstdlib>
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

class Driver final {
private:
    inline static const std::string DRIVER_PATH = "/sys/bus/hid/drivers/hid-multitouch";

    Driver() = default;

public:
    static Driver& getInstance()
    {
        static Driver inst;
        return inst;
    }

    Driver(const Driver&) = delete;
    Driver& operator=(const Driver&) = delete;

    ~Driver() = default;

    bool setTouchscreen(std::string device_id, bool status)
    {
        if (status)
            return system(("echo "+device_id+" > "+DRIVER_PATH+"/bind").c_str());
        else
            return system(("echo "+device_id+" > "+DRIVER_PATH+"/unbind").c_str());
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
