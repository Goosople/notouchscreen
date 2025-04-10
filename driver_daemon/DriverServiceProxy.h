
/*
 * This file was automatically generated by sdbus-c++-xml2cpp; DO NOT EDIT!
 */

#ifndef __sdbuscpp___home_goosople_notouchscreen_driver_daemon_DriverServiceProxy_h__proxy__H__
#define __sdbuscpp___home_goosople_notouchscreen_driver_daemon_DriverServiceProxy_h__proxy__H__

#include <sdbus-c++/sdbus-c++.h>
#include <string>
#include <tuple>

namespace top {
namespace goosople {
namespace notouchscreen {

class DriverService_proxy
{
public:
    static constexpr const char* INTERFACE_NAME = "top.goosople.notouchscreen.DriverService";

protected:
    DriverService_proxy(sdbus::IProxy& proxy)
        : m_proxy(proxy)
    {
    }

    DriverService_proxy(const DriverService_proxy&) = delete;
    DriverService_proxy& operator=(const DriverService_proxy&) = delete;
    DriverService_proxy(DriverService_proxy&&) = delete;
    DriverService_proxy& operator=(DriverService_proxy&&) = delete;

    ~DriverService_proxy() = default;

    void registerProxy()
    {
    }

public:
    bool switchTouchscreen(const std::string& device_id, const bool& status)
    {
        bool result;
        m_proxy.callMethod("switchTouchscreen").onInterface(INTERFACE_NAME).withArguments(device_id, status).storeResultsTo(result);
        return result;
    }

private:
    sdbus::IProxy& m_proxy;
};

}}} // namespaces

#endif
