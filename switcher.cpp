#include <fstream>
#include <string>
#include <iostream>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <cstring>
#include <cstdlib>

#define FIFO_PATH "/tmp/my_auto_fifo"

int main() {
    // remove existing FIFO
    unlink(FIFO_PATH);

    // create a new FIFO
    if (mkfifo(FIFO_PATH, 0666) == -1) {  // 权限设置为 0666（允许所有用户读写）
        std::cerr << "mkfifo 失败: " << strerror(errno) << std::endl;
        return 1;
    }

    // 3. 可选：显式设置权限（确保 umask 不影响）
    if (chmod(FIFO_PATH, 0666) == -1) {
        std::cerr << "chmod 失败: " << strerror(errno) << std::endl;
        unlink(FIFO_PATH);
        return 1;
    }

    std::cout << "等待客户端消息..." << std::endl;

    // 4. 以只读方式打开 FIFO（阻塞直到客户端以写方式打开）
    int fd = open(FIFO_PATH, O_RDONLY);
    if (fd == -1) {
        std::cerr << "open 失败: " << strerror(errno) << std::endl;
        unlink(FIFO_PATH);
        return 1;
    }

    // 5. 读取数据
    char buffer[1024];
    ssize_t bytes_read = read(fd, buffer, sizeof(buffer));
    if (bytes_read > 0) {
        buffer[bytes_read] = '\0';
        std::cout << "收到消息: " << buffer << std::endl;
    }

    char* env_driver_path = std::getenv("TOUCHSCREEN_DRIVER_PATH");
    std::string driver_path = (env_driver_path == NULL ? "/sys/bus/hid/drivers/hid-multitouch" : env_driver_path);
    std::ofstream bind(driver_path + "/bind");
    std::ofstream unbind(driver_path + "/unbind");

    // 6. 清理资源
    close(fd);
    unlink(FIFO_PATH);  // 删除 FIFO 文件

    return 0;
}