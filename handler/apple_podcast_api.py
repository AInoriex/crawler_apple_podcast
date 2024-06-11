from requests import get
from urllib3 import disable_warnings, exceptions
from os import path, remove
from random import randint
from traceback import format_exception # Python 3.10+
from urllib.parse import urlencode
from utils import user_agent
from utils.utime import get_now_time_string, random_sleep
from utils.logger import init_logger
from utils.file import download_url_resource_local, save_json_to_file, get_json_from_file
from utils.tool import load_cfg
from utils.lark import alarm_lark_text
from utils.cos import upload_file
from utils.ip import get_local_ip, get_public_ip
from utils.exception import ApplePodcastException

logger = init_logger("apple_podcast_api")
cfg = load_cfg("config.json")
disable_warnings(category=exceptions.InsecureRequestWarning)

class ApplePodReport:
    ''' 采集结果报告 '''
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
        self.report_time = get_now_time_string()
        self.public_ip = get_public_ip()
        succ = alarm_lark_text(cfg["lark_conf"]["webhook"], f"[ApplePodReport] 当前播客信息采集通知\
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
    # first request
    if "?" not in url: 
        params = {
            "l": "en-US", 
            "offset": "10"
        }
        url = url + "?" + urlencode(params)
        pod_report.reset()
    headers = {
        "User-Agent": user_agent.agents[randint(0, len(user_agent.agents)-1)],
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
        "Origin": "https://podcasts.apple.com",
        "Authorization": cfg["apple_procast_conf"]["Authorization"]
    }
    next_url = ""
    pod_report.set_extra_params("current_url", url)
    try:
        # logger.debug(f"ApplePodcastsHandler Request: {url} | {headers}")
        response = get(url=url, headers=headers, verify=False)
        # logger.debug(f"ApplePodcastsHandler Response: {response.status_code} | {response.content}")
        assert response.status_code == 200
        resp = response.json()

        applePod = ApplePodCrawler(url, resp)
        if "next" not in applePod.resp.keys():
            raise ApplePodcastException("key `next` not in response's keys")
        if "data" not in applePod.resp.keys():
            raise ApplePodcastException("key `data` not in response's keys")
        next_url = applePod.GetNextUrl()
        applePod.DownloadAudio()
        applePod.SaveJson()

        if not next_url.startswith("http"):
            next_url = "https://amp-api.podcasts.apple.com" + next_url

        pod_report.submit_report()
    except AssertionError:
        logger.error(f"ApplePodcastsHandler assert error, request {url} failed")
        raise ApplePodcastException(f"request {url} failed")
    except Exception as e:
        err = "".join(format_exception(e)).strip()
        logger.error(f"ApplePodcastsHandler Failed, error:{err}")
        raise e
    finally:
        logger.debug(f"ApplePodcastsHandler Result, next_url:{next_url}")
        return next_url

class ApplePodCrawler:
    ''' apple podcast采集'''
    def __init__(self, url:str, resp:dict):
        self.url = url
        self.user_id = self.GetUserId()
        self.resp = resp
        pod_report._user_id = self.user_id

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

    def ParseApiData(self)->list:
        ''' 解析响应体data字段,获取目标数据 '''
        # logger.debug(f"GetNextUrl Param, {self.resp}")
        if "data" not in self.resp.keys():
            logger.error("ParseApiData failed, no such `data` key in response.")
            return []
        res_list = []
        len_data = len(self.resp["data"])
        logger.info(f"ParseApiData 共获取到{len_data}条数据")
        pod_report._total_count += len_data
        try:
            for data in self.resp["data"]:
                res_list.append(self.ParseApiSingleData(data=data))
            logger.debug(f"ParseApiData Result List: {res_list}")
        except Exception as e:
            err = "".join(format_exception(e)).strip()
            logger.error(f"ParseApiData failed, error:{err}")
        finally:
            return res_list


    def ParseApiSingleData(self, data:dict)->dict:
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
        # logger.debug(f"ParseApiSingleData Param, {data}")
        info_dict = {
            "id": "Podcast_%s_%s"%(self.user_id, data["id"]),
            "title": data["attributes"]["name"],
            "full_url": data["attributes"]["url"],
            "author":data["attributes"]["artistName"],
            "duration": data["attributes"]["durationInMilliseconds"],
            "categories": data["attributes"]["genreNames"],
            "asset_url": data["attributes"]["assetUrl"]
        }
        logger.debug(f"ParseApiSingleData: {info_dict}")
        return info_dict

    def GetUserId(self)->str:
        ''' 获取用户id '''
        sub_str = self.url.rsplit("podcasts/")[1]
        res = sub_str.rsplit("/episodes")[0]
        return res

    def DownloadAudio(self)->bool:
        ''' 下载音频文件到本地 '''
        succ_count = 0
        fail_count = 0
        fail_list = []
        save_dir = cfg["common"]["download_path"]
        for data in self.resp["data"]:
            try:
                url = data["attributes"]["assetUrl"]
                pid = "Podcast_%s_%s"%(self.user_id, data["id"])
                sub_path = f"Podcast_{self.user_id}"
                # file_name = os.path.basename(url)
                file_name = pid + ".mp3"
                save_path = path.join(save_dir, sub_path, file_name) # 存储路径格式:/Podcast_203844864/Podcast_203844864_1000655529212.mp3
                if path.exists(save_path):
                    print(f"[Warn] 该路径下{save_path}文件存在，下载跳过")
                    continue
                # 文件下载本地
                succ = download_url_resource_local(url, save_path)
                if not succ:
                    fail_count += 1
                    fail_list.append(url)
                    pod_report._fail_count += 1
                    pod_report.add_fail_list(url)
                    logger.error(f"DownloadAudio handler failed, url:{url}")
                    continue
                # 上传cos
                cloud_path = "%s/%s/%s"%(cfg["cos_conf"]["save_path"], sub_path, file_name)
                _cloud_link = upload_file(from_path=save_path , to_path=cloud_path)
                # 移除本地文件
                remove(save_path)
                # TODO 数据库录入文件存储路径和文件信息
            except Exception as e:
                fail_count += 1
                fail_list.append(url)
                pod_report._fail_count += 1
                pod_report.add_fail_list(url)
                err = "".join(format_exception(e)).strip()
                logger.error(f"DownloadAudio failed, error:{err}")
                continue
            else:
                succ_count += 1
                pod_report._succ_count += 1
            finally:
                random_sleep(rand_st=10, rand_range=5)
        else:
            # alarm_lark_text(cfg["lark_conf"]["webhook"], f"Apple Podcast DownloadAudio Log \
            #     \n\tuser_id: {self.user_id} \
            #     \n\tlink: {self.url} \
            #     \n\tsucc_count: {succ_count} \
            #     \n\tfail_count: {fail_count} \
            #     \n\tfail_list: {fail_list}")
            return

    def SaveJson(self)->bool:
        add_list = self.ParseApiData()
        save_path = path.join(cfg["common"]["output_path"], "Podcast_"+self.user_id+".json")
        res_list = get_json_from_file(save_path)
        if res_list == None:
            res_list = []
        res_list += add_list
        save_succ = save_json_to_file(res_list, save_path=save_path)
        if not save_succ:
            logger.error("SaveJson save_json_to_file failed")
            logger.info("SaveJson data {output_json_list}")