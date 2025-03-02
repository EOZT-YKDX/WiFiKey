# WiFiKey
自动化爆破WiFi工具

一.项目介绍
1. 工具旨在帮助用户自动化处理WiFi相关指令，提高WiFi密码爆破效率和成功率。

二.项目信息
1. 项目版本：V5.15.2524
2. 最后更新：2025年2月12日

三.功能介绍
1. 环境检测 (environmental_detection)<br>
检测当前操作系统是否为Windows系统，确保脚本在兼容的环境中运行

2. 路径初始化 (initialize_paths)<br>
创建项目所需的各种目录结构<br>
包括日志目录、数据目录和WiFi配置文件目录

3. 日志配置 (setup_logging)<br>
设置日志记录器的级别和格式<br>
支持同时输出到控制台和日志文件

4. WiFi检测 (wifi_detection)<br>
使用Windows的netsh命令进行网络扫描，检测指定的SSID是否存在于当前可用的无线网络列表中

5. WiFi连接管理<br>
连接指定WiFi (connect_wifi)<br>
检查WiFi连接状态 (wifi_status)<br>
断开当前WiFi连接 (disconnect_wifi)<br>
添加WiFi配置文件 (add_configuration)<br>
移除WiFi配置文件 (remove_configuration)

6. WiFi配置文件生成 (build_configuration)<br>
根据SSID和密码生成XML格式的WiFi配置文件

7. 生成密码本 (generate_codebook)<br>
使用笛卡尔积生成指定长度的密码组合，支持自定义字符集和重复次数

8. 处理密码本 (handle_codebooks)<br>
去除重复行和无效密码（小于8位的密码）

9. WiFi爆破核心功能 (wifi_blasting)<br>
使用密码本对指定WiFi进行爆破<br>
包含详细的日志记录和进度跟踪<br>
支持断点续连，记录上次尝试的密码位置，支持自定义超时时间

10. 索引管理<br>
读取WiFi爆破进度索引 (read_index)<br>
写入WiFi爆破进度索引 (write_index)<br>
记录密码本路径、尝试时间、上次密码等信息

10. 主程序<br>
提供示例SSID和密码本路径，支持手动中断和异常处理，可切换日志级别

四.注意事项
1. 密码本需要用户自行准备或生成。
2. 使用前请确保获得目标网络的授权。
3. 目前仅支持Windows 10及以上系统。
4. 未经原作者授权，禁止用于其他用途。
5. 仅供研究学习使用，切勿用于非法途径。
