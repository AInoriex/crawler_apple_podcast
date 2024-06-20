# from requests import get
from urllib3 import disable_warnings, exceptions
from os import path, remove
from random import randint
from traceback import format_exception # Python 3.10+
from urllib.parse import urlencode
from json import dumps,loads
from utils import user_agent
from utils.utime import get_now_time_string, random_sleep
from utils.logger import init_logger
from utils.file import download_url_resource_local, save_json_to_file, get_json_from_file
from utils.tool import load_cfg
from utils.lark import alarm_lark_text
from utils.cos import upload_file
from utils.ip import get_local_ip, get_public_ip
from utils.exception import ApplePodcastException
from utils.request import retry_request_get
from db.data_download import DB as PipelineVideo

logger = init_logger("apple_podcast_api")
cfg = load_cfg("config.json")
disable_warnings(category=exceptions.InsecureRequestWarning)

class ApplePodReport:
    ''' 苹果播客采集结果报告 '''
    def __init__(self):
        self._user_id = ""
        self.local_ip = get_local_ip()
        self.public_ip = ""
        self._total_count = 0
        self._succ_count  = 0
        self._fail_count  = 0
        self._fail_list  = []
        self.extra_params = {}
        self.report_time = ""

    @property
    def user_id(self):   
        return self._user_id
    @user_id.setter 
    def user_id(self, v): 
        self._user_id = v
    
    @property
    def total_count(self):   
        return self._total_count
    @total_count.setter 
    def total_count(self, v): 
        self._total_count = v
    
    @property
    def succ_count(self):   
        return self._succ_count
    @succ_count.setter 
    def succ_count(self, v): 
        self._succ_count = v
    
    @property
    def fail_count(self):   
        return self._fail_count
    @fail_count.setter 
    def fail_count(self, v): 
        self._fail_count = v
    
    @property
    def fail_list(self)->list:   
        return self._fail_list
    def add_fail_list(self, v):
        self._fail_list.append(v)

    def reset(self):
        ''' 重置信息 '''
        self._user_id = ""
        self.public_ip = ""
        self._total_count = 0
        self._succ_count  = 0
        self._fail_count  = 0
        self._fail_list  = []
        self.extra_params = {}

    def set_extra_params(self, key, val):
        ''' 设置拓展字段 '''
        self.extra_params[key] = val

    def submit_report(self):
        ''' 飞书汇报信息 '''
        if self._user_id == "":
            return
        self.report_time = get_now_time_string()
        self.public_ip = get_public_ip()
        succ = alarm_lark_text(cfg["lark_conf"]["webhook"], f"[DEBUG] ApplePodReport采集通知\
            \n\t [用户信息] ID:{self._user_id} \
            \n\t [IP信息] local_ip: {self.local_ip} public_ip: {self.public_ip} \
            \n\t [状态计数] 当前一共{self._total_count}条, 成功:{self._succ_count}, 失败:{self._fail_count}\
            \n\t 失败列表: {self._fail_list} \
            \n\t [其他信息] {self.extra_params} \
            \n\t [汇报时间] {self.report_time}")
        if not succ:
            logger.error("ApplePodReport submit_report failed")

pod_report = ApplePodReport()

def ApplePodcastsHandler(url:str):
    ''' 获取&存储 Apple's Podcast 音频数据 
    @Params url:https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/1261944206/episodes?l=en-US&offse=20; 
    '''
    # logger.debug(f"ApplePodcastsHandler params, url:{url}")
    if url == "":
        logger.warning("ApplePodcastsHandler params invalid, empty url")
        return ""

    # new user first request init
    if "?" not in url: 
        params = {
            "l": "en-US", 
            "offset": "10"
        }
        url = url + "?" + urlencode(params)
        pod_report.submit_report()
        pod_report.reset()
    pod_report.set_extra_params("current_url", url)

    try:
        # 请求接口获取当前页JSON数据
        # logger.debug(f"ApplePodcastsHandler Request: {url} | {headers}")
        headers = {
            "User-Agent": user_agent.agents[randint(0, len(user_agent.agents)-1)],
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close",
            "Origin": "https://podcasts.apple.com",
            "Authorization": cfg["apple_procast_conf"]["Authorization"]
        }
        # response = get(url=url, headers=headers, verify=False)
        # assert response.status_code == 200
        response = retry_request_get(url=url, headers=headers, verify=False, retry=3)
        # logger.debug(f"ApplePodcastsHandler Response: {response.status_code} | {response.content}")

        # 接口响应默认utf-8编码, JSON序列化
        # resp = response.json()
        data = response.content.decode('utf-8', 'ignore')  # 忽略非法字符
        resp = loads(data)

        applePod = ApplePodCrawler(url, resp)
        # 解析下载data数据
        if "data" not in applePod.resp.keys():
            raise ApplePodcastException("key `data` not in response's keys")
        applePod._len_data = len(applePod.resp["data"])
        pod_report.set_extra_params("len_of_data", applePod._len_data)
        while 1:
            try:
                applePod.GetNextData()
                if applePod.index < 0 or applePod.now_data == {}:
                    logger.warn(f"ApplePodCrawler's data process done. user_id:{applePod.user_id}")
                    break
                applePod.ParseApiSingleData()
                applePod.DownloadSingleAudio()
                applePod.CreateRecordToGkdDatabase()
                applePod.SaveJson()
            except Exception as e:
                err = "".join(format_exception(e)).strip()
                logger.error(f"ApplePodCrawler Failed, error:{err} user_id:{applePod.user_id}")
                # alarm_lark_text(
                #     webhook = cfg["lark_conf"]["webhook"], 
                #     text = f"[ERROR] 播客下载失败 user_id:{applePod.user_id} \
                #         \n\terror:{err} \
                #         \n\tindex:{applePod.index} \
                #         \n\tnow_data:{applePod.now_data}"
                # )
                pod_report.fail_count += 1
                pod_report.add_fail_list(applePod.src_link)
                continue
            else:
                pod_report.succ_count += 1
            finally:
                pod_report.total_count += 1
                # pod_report.submit_report()
                random_sleep(rand_st=10, rand_range=10)

        # 获取下页data链接
        if "next" not in applePod.resp.keys():
            logger.warn("获取不到下一条链接，采集结束")
            url = ""
        else:
            url = applePod.GetNextUrl()
            if not url.startswith("http"):
                url = "https://amp-api.podcasts.apple.com" + url

    except AssertionError:
        logger.error(f"ApplePodcastsHandler assert error, request {url} failed")
        pod_report.set_extra_params("resp.status_code", response.status_code)
        pod_report.set_extra_params("resp.content", response.content)
        raise ApplePodcastException(f"request {url} failed")
    except Exception as e:
        err = "".join(format_exception(e)).strip()
        logger.error(f"ApplePodcastsHandler Failed, error:{err}")
        alarm_lark_text(
            webhook = cfg["lark_conf"]["webhook"], 
            text = f"[ERROR] 播客当前批次处理出现未知错误 user_id:{applePod.user_id} \
                \n\terror:{err} \
                \n\tindex:{applePod.index} \
                \n\tnow_data:{applePod.now_data}"
        )
        raise e
    else:
        logger.debug(f"ApplePodcastsHandler Done, next_url:{url}")
        return url

class ApplePodCrawler:
    ''' 苹果播客爬虫 '''
    def __init__(self, url:str, resp:dict):
        self.url = url
        self.resp = resp

        self._user_id = self.GetUserId() # 用户id
        self._len_data = 0 # resp.data长度
        self._now_data = {} # 当前处理的data
        self._index = -1 # 当前处理data索引

        self._vid = 0 # 视频id
        self._link = "" # 详情页链接
        self._src_link = "" # 下载链接
        self._cloud_link = "" # 云端链接
        self._duration = 0 # MP3时长(秒)
        self._info_dict = {}

        pod_report._user_id = self._user_id
        pass

    @property
    def user_id(self):   
        return self._user_id
    @property
    def len_data(self):   
        return self._len_data
    @property
    def now_data(self):   
        return self._now_data
    @property
    def src_link(self):   
        return self._src_link

    @property
    def index(self):   
        return self._index
    @index.setter 
    def index(self, v): 
        self._index = v
    
    
    def GetNextUrl(self)->str:
        ''' 获取下一页链接 '''
        # logger.debug(f"GetNextUrl Param, {self.resp}")
        if "next" not in self.resp.keys():
            logger.error("GetNextUrl failed, no such `next` key in response.")
            return ""
        if not isinstance(self.resp['next'], str):
            logger.error(f"GetNextUrl failed, resp['next'] value invalid. val:{self.resp['next']}")
            return ""
        return self.resp["next"]

    def ParseApiSingleData(self)->dict:
        ''' 解析单个data数据 '''
        ''' example json
        {
            "id": "Podcast_1261944206_1000391903336",
            "title": "Billionaire Boss Baby Brain Genius (ft Alex Kealy)",
            "full_url": "https://podcasts.apple.com/us/podcast/billionaire-boss-baby-brain-genius-ft-alex-kealy/id1261944206?i=1000391903336",
            "author": "TRASHFUTURE",
            "duration": 5091000,
            "categories": ["Comedy"],
            "tags": [],
            "view_count": "null",
            "assetUrl": "https://mcdn.podbean.com/mf/web/dqdqn9/Episode_Toddler_Edits_again_-_03_09_2017_21_15.mp3"
        }'''
        logger.debug(f"ParseApiSingleData Param, user_id:{self._user_id}, now_data:{self._now_data}")
        if "durationInMilliseconds" not in self._now_data["attributes"].keys():
            self._now_data["attributes"]["durationInMilliseconds"] = 0
        info_dict = {
            "id": "Podcast_%s_%s"%(self._user_id, self._now_data["id"]),
            "title": self._now_data["attributes"]["name"],
            "full_url": self._now_data["attributes"]["url"],
            "author":self._now_data["attributes"]["artistName"],
            "duration": self._now_data["attributes"]["durationInMilliseconds"] / 1000,
            "categories": self._now_data["attributes"]["genreNames"],
            "asset_url": self._now_data["attributes"]["assetUrl"]
        }
        self._vid = info_dict["id"] # 视频id
        self._link = info_dict["full_url"] # 详情页链接
        self._src_link = info_dict["asset_url"] # 下载链接
        self._duration = info_dict["duration"] # MP3时长(秒)
        self._info_dict = info_dict
        logger.debug(f"ParseApiSingleData: {info_dict}")

    def GetUserId(self)->str:
        ''' 获取用户id '''
        sub_str = self.url.rsplit("podcasts/")[1]
        res = sub_str.rsplit("/episodes")[0]
        return res

    def DownloadSingleAudio(self):
        ''' 下载&上传单个MP3 '''
        try:
            save_dir = cfg["common"]["download_path"] # 存储路径: {配置文件路径}/Podcast_203844864/Podcast_203844864_1000655529212.mp3
            pid = self._vid
            url = self._src_link
            sub_path = f"Podcast_{self._user_id}"
            file_name = pid + ".mp3"
            save_path = path.join(save_dir, sub_path, file_name) 
            if path.exists(save_path):
                print(f"[Warn] 该路径下{save_path}文件存在，下载跳过")
                return
            # 文件下载本地
            succ = download_url_resource_local(url, save_path)
            if not succ:
                raise ApplePodcastException("download mp3 not succ, download_url_resource_local failed")
            # 上传cos
            cloud_path = "%s/%s/%s"%(cfg["cos_conf"]["save_path"], sub_path, file_name)
            _cloud_link = upload_file(from_path=save_path , to_path=cloud_path)
            if _cloud_link == "":
                raise ApplePodcastException("cloud link is null, upload_file failed")
            self._cloud_link = _cloud_link
            # 移除本地文件
            remove(save_path)
        except Exception as e:
            # err = "".join(format_exception(e)).strip()
            # logger.error(f"DownloadSingleAudio unexpected error:{err}")
            raise e
        finally:
            pass

    def SaveJson(self)->bool:
        ''' 解析结果json存储到本地文件 '''
        add_json = self._info_dict
        if add_json == {}:
            logger.warn(f"SaveJson self._info_dict is empty, index:{self._index}")
            return False
        save_path = path.join(cfg["common"]["output_path"], "Podcast_"+self._user_id+".json")
        res_list = get_json_from_file(save_path)
        if res_list == None:
            res_list = []
        res_list.append(add_json)
        save_succ = save_json_to_file(res_list, save_path=save_path)
        if not save_succ:
            logger.error(f"SaveJson save_json_to_file failed, {res_list}")
        return save_succ

    def CreateRecordToGkdDatabase(self)->bool:
        ''' 港科大数据库新增播客数据记录 '''
        PipelineVideo.CreatePodcastRecord (
            vid=self._vid,
            cloud_path=self._cloud_link,
            duration=self._duration,
            link=self._link,
            info=dumps(self._info_dict)
        )

    def GetNextData(self):
        ''' 获取下一个data数据 '''
        try:
            self._index += 1
            if self._index >= self._len_data:
                self._index = -1
                self._now_data = {}
            else:
                self._now_data = self.resp["data"][self._index]
                print(f"[进度] URL:{self.url} | Now:{self._index}/{self._len_datas}")
        except Exception as e:
            self._index = -1
            self._now_data = {}
        finally:
            self._vid = 0 # 视频id
            self._link = "" # 详情页链接
            self._src_link = "" # 下载链接
            self._duration = 0 # MP3时长(秒)
            self._cloud_link = "" # 云端链接
            self._info_dict = {} # 存储结构体