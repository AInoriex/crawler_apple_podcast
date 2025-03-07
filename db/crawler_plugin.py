import os
import requests
import time
from uuid import uuid4
from utils.logger import logger

# _status_code = -10100
# _error_MSG = "采集视频失败：代理节点出现人机验证 - Sign in to confirm you’re not a bot."
# _status_code = -10200
# _error_MSG = "采集视频失败：代理节点失效 - Failed to extract any player response."
# _status_code = -10300
# _error_MSG = "采集视频失败：视频有年龄限制，需要登录验证年龄 - Sign in to confirm your age."
# _status_code = -99100
# _error_MSG = "采集视频失败：其他异常"
CrawlerPluginErrorCodeMap = {
    "ErrorCodeSuccess": {
        "status_code": 200,
        "error_msg": "采集视频成功"
    },
    "ErrorCodeBotVerify": {
        "status_code": -10100,
        "error_msg": "采集视频失败：代理节点出现人机验证 - Sign in to confirm you’re not a bot."
    },
    "ErrorCodeProxyUnavaliable": {
        "status_code": -10200,
        "error_msg": "采集视频失败：代理节点失效 - Failed to extract any player response."
    },
    "ErrorCodeAgeVerify": {
        "status_code": -10300,
        "error_msg": "采集视频失败：视频有年龄限制，需要登录验证年龄 - Sign in to confirm your age."
    },


    "ErrorCodeUnknownException": {
        "status_code": -99100,
        "error_msg": "采集视频失败：其他异常"
    },
}

def generate_meta_id(sub_text:str):
    uid = str(uuid4())
    if sub_text != "":
        uid = f"{uid}_{sub_text}"
    return uid

def send_json_2_server(meta_dict:dict, process_name:str, status:str, status_code:int, error_msg:str):
    """回调任务数据到服务端，阻塞保证上报成功再Return

    Args:
        meta_dict (dict): the dict of meta data
        process_name (str): The name of the process.
        status (str): The status of the download, e.g. "success" or "failed".
        status_code (int): The status code of the download, e.g. 200 for success.
        error_msg (str): The error message of the download, if any.

    Returns:
        None
    """
    # # ----- 测试数据 HARDCODE -----
    # logger.info(f"自测跳过回调，meta_dict:{meta_dict}, process_name:{process_name}, status:{status}, status_code:{status_code}, error_msg:{error_msg}")
    # return
    # # ----- 测试数据 HARDCODE -----

    crwaler_platform_web_url = os.getenv("CRWALER_PLATFORM_WEB_URL", "")
    url = crwaler_platform_web_url + "/crawler-platform/report_download_result"
    headers = {'Content-Type': 'application/json'}
    request_data = {
        "processName": process_name,
        "downloadStatus": status,
        "downloadStatusCode": status_code,
        "errorMsg": error_msg,
        "data": meta_dict
    }
    logger.info(f"回传资源下载结果请求参数, url:{url}, data:{request_data}")

    #阻塞直到信息汇报成功才进入下一个任务
    while 1:
        try:
            response = requests.post(url, json=request_data, headers=headers)
            if response.status_code != 200:
                logger.error(f"回传资源下载结果的失败，状态码: {response.status_code}, 请重试")
                continue
            json_data = response.json()
            if json_data["code"] != 200:
                logger.error(f"回传资源下载结果的失败，msg:{json_data['msg']}, 请重试")
                continue
        except Exception as e:
            logger.error(f"回传资源下载结果未知错误，{e}")
        else:
            logger.info("回传资源下载结果的成功")
            return
        finally:
            time.sleep(2)

class VideoMeta:
    crwaler_platform_web_url = os.getenv("CRWALER_PLATFORM_WEB_URL", "")
    cloud_path = os.getenv("CLOUD_SAVE_PATH", "")

    # is_success定义
    isSuccessTrue = 0   # 0 成功
    isSuccessFalse = 1  # 1 失败

    def __init__(self, video_id, type, is_success, storage_location, 
            title="", subject=[], description="", source_url="", 
            file_size=-1, file_type="", compression_method="", duration=-1, categories=[], 
            view_count=-1, comment_count=-1, like_count=-1, channel="", channel_follower_count=-1, 
            uploader="", uploader_id="", uploader_url="", upload_date="", duration_string="", 
            width=-1, height=-1, resolution="", fps=-1, input_lake_source="爬虫", download_url=""):
        
        """
        VideoMeta is a class that is used to contain the information of a video.

        Parameters
        ----------
        video_id : str
            视频id
        is_success : int
            下载是否成功 0-成功 1-失败
        type : str
            数据类型（视频、音频、文本）
        storage_location : str
            文件在obs的存储位置，平台侧传目录，插件在后面拼接文件名形成全路径
        title : str
            标题
        subject : list     
            主题（Subject） 资源内容的主题描述 
        description : str     
            资源内容的解释描述
        source_url : str     
            视频来源url
        file_size : str     
            数据文件大小（单位：byte）
        file_type : str     
            数据文件的类型，如CSV、TEXT、DOC,JPG,MP3,MP4,AVI等
        compression_method : str     
            压缩方式 (Compression method ) 数据文件的压缩方式，如WinRAR、7-Zip、Keka等
        duration : int     
            视频时长 视频时长（单位：秒）
        categories : list     
            分类
        view_count : int     
            观看数
        comment_count : int     
            评论数
        like_count : int     
            点赞数
        channel : str     
            频道名
        channel_follower_count : int     
            频道关注数
        uploader : str     
            上传者
        uploader_id : str     
            上传者的唯一id
        uploader_url : str     
            上传者的主页
        upload_date : str     
            上传时间
        duration_string : str     
            视频时长 - 换算为时分秒
        width : int     
            视频分辨率 - 长
        height : int     
            视频分辨率 - 高
        resolution : str     
            视频分辨率 - 长X高 的形式
        fps : int     
            视频帧率
        input_lake_source : str
            默认"爬虫"
        download_url : str
            音频下载链接（采集插件内部使用）
        """
        self.video_id = video_id
        self.type = type
        self.is_success = is_success
        self.storage_location = storage_location
        self.title = title
        self.subject = subject
        self.description = description
        self.source_url = source_url
        self.file_size = file_size
        self.file_type = file_type
        self.compression_method = compression_method
        self.duration = duration
        self.categories = categories
        self.view_count = view_count
        self.comment_count = comment_count
        self.like_count = like_count
        self.channel = channel
        self.channel_follower_count = channel_follower_count
        self.uploader = uploader
        self.uploader_id = uploader_id
        self.uploader_url = uploader_url
        self.upload_date = upload_date
        self.duration_string = duration_string
        self.width = width
        self.height = height
        self.resolution = resolution
        self.fps = fps
        self.input_lake_source = input_lake_source
        self.download_url = download_url

    def dict(self):
        return {
            "video_id": self.video_id,
            "type": self.type,
            "is_success": self.is_success,
            "storage_location": self.storage_location,
            "title": self.title,
            "subject": self.subject,
            "description": self.description,
            "source_url": self.source_url,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "compression_method": self.compression_method,
            "duration": self.duration,
            "categories": self.categories,
            "view_count": self.view_count,
            "comment_count": self.comment_count,
            "like_count": self.like_count,
            "channel": self.channel,
            "channel_follower_count": self.channel_follower_count,
            "publisher": self.uploader,
            "p_id": self.uploader_id,
            "uploader_url": self.uploader_url,
            "upload_date": self.upload_date,
            "duration_string": self.duration_string,
            "width": self.width,
            "height": self.height,
            "resolution": self.resolution,
            "fps": self.fps,
            "input_lake_source": self.input_lake_source,
        }

    def __str__(self) -> str:
        return (
            f"VideoMeta(video_id={self.video_id}, type={self.type}, is_success={self.is_success}, storage_location={self.storage_location}, "
            f"title={self.title}, subject={self.subject}, description={self.description}, source_url={self.source_url}, file_size={self.file_size}, "
            f"file_type={self.file_type}, compression_method={self.compression_method}, duration={self.duration}, categories={self.categories}, "
            f"view_count={self.view_count}, comment_count={self.comment_count}, like_count={self.like_count}, channel={self.channel}, "
            f"channel_follower_count={self.channel_follower_count}, publisher={self.uploader}, p_id={self.uploader_id}, "
            f"uploader_url={self.uploader_url}, upload_date={self.upload_date}, duration_string={self.duration_string}, "
            f"width={self.width}, height={self.height}, resolution={self.resolution}, fps={self.fps}, input_lake_source={self.input_lake_source})"
        )

    def report_server(self, process_name, status, status_code, error_msg):
        """回调任务数据到服务端，阻塞保证上报成功再Return

        Args:
            process_name (str): The name of the process.
            status (str): The status of the download, e.g. "success" or "failed".
            status_code (int): The status code of the download, e.g. 200 for success.
            error_msg (str): The error message of the download, if any.

        Returns:
            None

        Raises:
            Exception: If the report fails.
        """
        url = self.crwaler_platform_web_url + "/crawler-platform/report_download_result"
        headers = {'Content-Type': 'application/json'}
        _item = self.dict()
        request_data = {
            "processName": process_name,
            "downloadStatus": status,
            "downloadStatusCode": status_code,
            "errorMsg": error_msg,
            "data": _item
        }
        logger.info(f"回传资源下载结果请求参数, url:{url}, data:{request_data}")

        #阻塞直到信息汇报成功才进入下一个任务
        while 1:
            try:
                response = requests.post(url, json=request_data, headers=headers)
                if response.status_code != 200:
                    logger.error(f"回传资源下载结果的失败，状态码: {response.status_code}, 请重试")
                    continue
                json_data = response.json()
                if json_data["code"] != 200:
                    logger.error(f"回传资源下载结果的失败，msg:{json_data['msg']}, 请重试")
                    continue
            except Exception as e:
                logger.error(f"回传资源下载结果未知错误，{e}")
            else:
                logger.info("回传资源下载结果的成功")
                return
            finally:
                time.sleep(2)

