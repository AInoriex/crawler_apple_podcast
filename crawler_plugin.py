import os
import tempfile
from pathlib import Path
from utils.logger import logger
from utils.obs import upload_file_v2
from utils.request import download_resource
from utils.file import get_file_size
from utils.utime import get_now_day_string_short
from handler.apple_podcast_audio import apple_podcast_plugin_handler
# from handler.apple_podcast_audio import apple_podcast_plugin_handler_api, apple_podcast_plugin_handler_web
from db.crawler_plugin import send_json_2_server, CrawlerPluginErrorCodeMap, VideoMeta

def extract_obs_url_info(obs_url:str):
    # input obs://{bucket_name}/path/to/file.txt
    # input obs:/{bucket_name}/path/to/file.txt
    # output bucket_name, path/to/file.txt
    if not obs_url.startswith("obs:"):
        return "", obs_url
    # remove obs:
    obs_url = obs_url.replace("obs:", "", 1)
    # remove // or /
    obs_url = obs_url.replace("//", "", 1)
    if obs_url.startswith("/"):
        obs_url = obs_url[1:]
    # return bucket_name, obs_save_path
    return obs_url.split("/", 1)[0], obs_url.split("/", 1)[1]

def apple_podcast_crawler_plugin(url, other_data=None, worker_id="0", server_name="apple_podcast_worker_0"):
    """
    Apple Podcast下载插件处理逻辑，流程为解析网页->下载资源->上传云端->聚合信息->回调数据中心

    :param url: Apple Podcast 音频url
    :param other_data: 其他meta信息
    :param worker_id: 工作进程id
    :param server_name: 工作进程的名称
    :return: None
    """
    try:
        logger.info(f"[{server_name}进程] Process:{worker_id} | url:{url}, other_data:{other_data} | 开始苹果播客Apple Podcast下载任务 ...")
        report_dict = {}
        storage_location = other_data.get("storage_location", "")

        # 解析音频信息
        video_info:VideoMeta = apple_podcast_plugin_handler(url)
        
        # 下载音频
        with tempfile.TemporaryDirectory() as local_save_folder:
            download_url = video_info.download_url
            filename = f"{video_info.video_id}.mp3"
            local_save_path = os.path.join(local_save_folder, filename) # 本地文件路径
            local_save_path = download_resource(download_url, local_save_path, proxies=None)

            # 上传obs, 获取完整路径cloud_url
            # 云端文件路径新增一级存储目录 cloud_save_folder/{日期}/filename
            cloud_url = ""
            bucket_name, cloud_save_folder = extract_obs_url_info(storage_location)
            cloud_save_path = Path(cloud_save_folder, get_now_day_string_short(), filename).as_posix()
            if bucket_name != "":
                cloud_url = upload_file_v2(from_path=local_save_path, to_path=cloud_save_path, urlBase=f"obs://{bucket_name}/")
            else:
                cloud_url = upload_file_v2(from_path=local_save_path, to_path=cloud_save_path, urlBase=storage_location)
            
            # 更新meta信息
            video_info.storage_location = cloud_url
            video_info.file_size = int(get_file_size(local_save_path)) * 1024 # MB*1024->Bytes
            video_info.is_success = 0

            # 删除临时文件
            os.remove(local_save_path)

        # 如果有旧meta信息则合并二者meta信息
        report_dict = video_info.dict()
        if other_data: 
            try:
                report_dict.update(other_data)
                report_dict["storage_location"] = cloud_url
            except Exception as e:
                logger.error(f"[{server_name}进程] Process:{worker_id} | url:{url} | 更新meta信息失败，{e}，video_info:{video_info.dict()}, other_data:{other_data}")
                # return False

        # 回调上报meta信息
        # video_info.report_server(
        #     process_name=f'{server_name}-{worker_id}',
        #     status="success",
        #     status_code=200,
        #     error_msg="",
        # )
        send_json_2_server(
            meta_dict=report_dict,
            process_name=f'{server_name}-{worker_id}',
            status="success",
            status_code=CrawlerPluginErrorCodeMap["ErrorCodeSuccess"]["status_code"],
            error_msg=CrawlerPluginErrorCodeMap["ErrorCodeSuccess"]["error_msg"],
        )
        logger.info(f"[{server_name}进程] Process:{worker_id} | url:{url} | 下载状态及信息回传数据完成")

        return True
    except Exception as e:
        logger.error(f"[{server_name}进程] Process:{worker_id} | url:{url} | 任务失败，{e}")
        send_json_2_server(
            meta_dict=report_dict,
            process_name=f'{server_name}-{worker_id}',
            status="fail",
            status_code=CrawlerPluginErrorCodeMap["ErrorCodeUnknownException"]["status_code"],
            error_msg=CrawlerPluginErrorCodeMap["ErrorCodeUnknownException"]["error_msg"]+str(e),
        )
        return False
