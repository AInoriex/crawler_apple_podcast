import os
import time
import requests
import threading
import configparser
from pathlib import Path
# from loguru import logger
from dotenv import load_dotenv
from multiprocessing import Process
from utils.logger import logger
# from yt_dlp_down_core import start_task
from crawler_plugin import apple_podcast_crawler_plugin

load_dotenv()

config = configparser.ConfigParser()

BUSY_FLAG = False
SOURCE_URL = ""

_hostname = os.getenv("HOSTNAME")
_env_proxy = os.getenv("PROXY")
crwaler_platform_web_url = os.getenv("CRWALER_PLTFORM_WEB_URL")


# def get_single_task(process_name, source_type="youtube"):
def get_single_task(process_name, source_type="apple_podcast"):
    param = "processName={}&sourceType={}".format(process_name, source_type)
    url = crwaler_platform_web_url + "/crawler-platform/get_download_url?" + param
    # logger.info(f"进程:{process_name}拿到资源下载需求的url:{url}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data["data"] is None:
                return None, None, 0, "没有资源下载的需求"
            if data["code"] == 200:
                # result = {"source_url": data["data"]["source_url"],
                #           "source_type": data["data"]["source_type"]}
                _data = data["data"]
                # 验证数据的必需字段
                if "source_url" not in _data:
                    error_message = {"error": "字段缺失", "details": "'source_url' 是必须的"}
                    return None, None, -1301, error_message

                if "storage_location" not in _data:
                    error_message = {"error": "字段缺失", "details": "'storage_location' 是必须的"}
                    return None, None, -1302, error_message

                url = _data.pop("source_url", None)
                return url, _data, 200, f"接收到请求：{_data}"
            else:
                # print("获取资源下载需求的失败,msg:{}", data["msg"])
                return None, None, -1303, f"获取资源下载需求的失败,code:{data['code']}，msg:{data['msg']}"
        else:
            # print(f"获取资源下载需求的失败，状态码: {response.status_code}")
            return None, None, -1304, f"status_code={response.status_code}"
    except Exception as e:
        # logger.error(f"获取资源下载需求的失败，错误：{e}")
        return None, None, -1305, f"code_error:{e}"


def check_proxy_can_use():
    try:
        # 如果文件存在，说明触发了bot验证，因此取反
        _path = "./conf/proxy_can_use_flag.json"
        file_path = Path(_path)
        return not file_path.is_file()
    except Exception as e:
        return True


def del_proxy_flag():
    _path = "./conf/proxy_can_use_flag.json"
    file_path = Path(_path)
    if file_path.is_file():
        try:
            file_path.unlink()  # 删除文件
            logger.info(f"保存代理错误Flag文件已清除: {file_path}")
        except Exception as e:
            logger.error(f"删除文件失败：{e}")


def get_current_timestamp():
    return int(time.time() * 1000)


def heartbeat(interval, process_name):
    global BUSY_FLAG
    global SOURCE_URL

    # ----- 测试数据 HARDCODE -----
    print("自测跳过心跳上报")
    logger.info("自测跳过心跳上报")
    return
    # ----- 测试数据 HARDCODE -----

    """子线程函数，用于定时回报心跳。"""
    while True:
        # print(f"心跳: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(interval)

        url = crwaler_platform_web_url + "/crawler-platform/report_crawler_heartbeat"
        # print("上报爬虫进程心跳url:{}", url)

        param = {
            "processName": process_name,
            "crawlerType": "youtube",
            "crawlerTypeDesc": "采集youtube网站视频",
            "crawlerStatus": "busy" if BUSY_FLAG else "idle",
            "sourceUrl": SOURCE_URL
        }
        # print(param)
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, json=param, headers=headers)
        try:
            if response.status_code == 200:
                data = response.json()
                if data["code"] == 200:
                    # logger.info(f"进程:{process_name}心跳上报成功")
                    pass
                else:
                    logger.error(f"进程:{process_name}心跳上报失败,msg:{data['msg']}")
            else:
                logger.error(f"进程:{process_name}心跳上报失败，状态码: {response.status_code}")
        except Exception as e:
            logger.error(f"进程:{process_name}心跳上报失败，错误: {e}")


def worker_process(worker_id, server_flag, start_time=str(get_current_timestamp())):
    global BUSY_FLAG
    global SOURCE_URL
    SOURCE_URL = ""
    # 创建一个子线程，每隔3秒回报一次心跳
    heartbeat_thread = threading.Thread(target=heartbeat, args=(3, f"{server_flag}-{worker_id}-{start_time}"),
                                        daemon=True)
    heartbeat_thread.start()

    logger.info(f"# {server_flag} - 进程 - {worker_id} # 启动")
    show_Msg = show_Net_ErMsg = show_Core_ErMsg = Show_Param_ErMSG = True
    while True:
        time.sleep(1)  # 控制任务调度的频率
        try:
            result = False
            # source_url, task_data, status_code, _MSG = get_single_task(f"{server_flag}-{worker_id}-{start_time}")
            
            # ----- 测试数据 HARDCODE -----
            source_url= "https://podcasts.apple.com/us/podcast/2281-elon-musk/id360084272?i=1000696846801"
            task_data = {"storage_location":"/multimodel.db/apple_podcast/"}
            status_code = 200
            _MSG = "ok"
            # ----- 测试数据 HARDCODE -----

            # 0 "没有资源下载的需求"
            # 200 f"接收到请求：{_data}"
            # -1301 {"error": "字段缺失", "details": "'source_url' 是必须的"}
            # -1302 {"error": "字段缺失", "details": "'storage_location' 是必须的"}
            # -1303, f"获取资源下载需求的失败,code:{data['code']}，msg:{data['msg']}"
            # -1304, f"status_code={response.status_code}"
            # -1305, f"code_error:{e}"
            # 消息显示，确保错误消息只显示一次
            if status_code == 200:
                logger.info(f"# {server_flag} - 进程 - {worker_id} # {_MSG}")
                BUSY_FLAG = True
                SOURCE_URL = source_url
                result = apple_podcast_crawler_plugin(
                    url=source_url,
                    other_data=task_data,
                    worker_id=f'{worker_id}-{start_time}',
                    server_name=server_flag,
                )
                show_Msg = show_Net_ErMsg = show_Core_ErMsg = Show_Param_ErMSG = True
            elif status_code == 0:
                if show_Msg:
                    logger.info(f"# {server_flag} - 进程 - {worker_id} # {_MSG}")
                    show_Msg = False
                show_Net_ErMsg = show_Core_ErMsg = Show_Param_ErMSG = True
            elif status_code in [-1301, -1302]:
                if Show_Param_ErMSG:
                    logger.error(_MSG)
                    Show_Param_ErMSG = False
                    show_Msg = show_Net_ErMsg = show_Core_ErMsg = True
            elif status_code in [-1303, -1304]:
                if show_Net_ErMsg:
                    logger.error(_MSG)
                    show_Net_ErMsg = False
                    show_Msg = show_Core_ErMsg = Show_Param_ErMSG = True
            else:
                if show_Core_ErMsg:
                    logger.error(_MSG)
                    show_Core_ErMsg = False
                    show_Msg = show_Net_ErMsg = Show_Param_ErMSG = True

            # 重置心跳参数
            BUSY_FLAG = False
            SOURCE_URL = ""

            if check_proxy_can_use():
                # 正常情况下
                time.sleep(1)  # 控制任务调度的频率
            else:
                if result:
                    # 如果下载成功了，就把flag文件删除
                    del_proxy_flag()
                if status_code == 0:
                    # 下载完成，没东西了，也把flag文件删除
                    del_proxy_flag()
                else:
                    # 触发了验证
                    logger.info(f"# {server_flag} - 进程 - {worker_id} # 检测到触发了bot验证，将十分钟进行一次下载尝试")
                    time.sleep(3 * 60)  # 控制任务调度的频率
        except Exception as e:
            logger.error(f"进程 {worker_id} 遇到错误: {e}")
            break  # 出现异常退出循环


def monitor_processes():
    server_flag = _hostname if _hostname else "mycomputer1"
    logger.info(f"本机唯一标识：{server_flag}")
    # 删除代理错误flag文件
    del_proxy_flag()
    config.read("./conf/config.ini", encoding="utf-8")
    if _env_proxy:
        config.set('proxy', 'proxy', _env_proxy)
    PROCESS_COUNT = config.get("process", "process_count")
    processes = {}
    for i in range(int(PROCESS_COUNT)):
        start_time = get_current_timestamp()
        p = Process(target=worker_process, args=(i, server_flag, start_time))
        p.start()
        processes[i] = p
        # 避免一次性拉起太多导致代理接口奔溃
        time.sleep(10)

    while True:
        for i, p in processes.items():
            if not p.is_alive():  # 如果子进程已退出
                logger.warning(f"进程 {i} 已退出，正在重新启动...")
                start_time = get_current_timestamp()
                new_p = Process(target=worker_process, args=(i, server_flag, start_time))
                new_p.start()
                processes[i] = new_p
        time.sleep(5)  # 每隔 5 秒检查一次


if __name__ == "__main__":
    monitor_processes()
