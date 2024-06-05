import os
import json
import random
import requests
from urllib.parse import urlencode
from utils import user_agent
from utils.utime import get_now_time_string_short, random_sleep
from utils.logger import init_logger
from utils.file import download_url_resource_local
from utils.tool import load_cfg
from utils.lark import alarm_lark_text
from utils.cos import upload_file

logger = init_logger("apple_podcast_api")
cfg = load_cfg("config.json")

def ApplePodcastsHandler(url:str, params:dict):
    ''' 获取&存储 Apple's Podcast 音频数据 
    @Params url:https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/1261944206/episodes; 
    @Params params:{"l"="en-US";"offset"="20"};
    '''
    logger.debug(f"ApplePodcastsHandler params, url:{url}, params:{params}")
    if url == "":
        logger.error("ApplePodcastsHandler params invalid, empty url")
        return
    # url = "https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/1261944206/episodes?l=en-US&offset=20"
    if len(params) <= 0 : #第一次请求
        params = {
            "l": "en-US", 
            "offset": "10"
        }
    headers = {
        "User-Agent": user_agent.agents[random.randint(0, len(user_agent.agents)-1)],
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
        "Origin": "https://podcasts.apple.com",
        "Authorization": cfg["apple_procast_conf"]["Authorization"]
    }
    next_url = ""
    res_list = []
    try:
        # logger.debug(f"ApplePodcastsHandler Request: {url} | {params} | {headers}")
        response = requests.get(url, headers=headers, params=params, verify=False)
        # logger.debug(f"ApplePodcastsHandler Response: {response.status_code} | {response.content}")
        # if response.status_code != 200:
        #     logger.error(f"ApplePodcastsHandler request failed, response:{response.status_code} | {response.content}")
        #     return "", []
        assert response.status_code == 200
        resp = response.json()

        applePod = ApplePod(url, params, resp)
        next_url = applePod.GetNextUrl()
        res_list = applePod.ParseApiData()
        if len(res_list) > 0:
            applePod.DownloadAudio()
        if not next_url.startswith("http"):
            next_url = "https://amp-api.podcasts.apple.com" + next_url
    except Exception as e:
        logger.error(f"ApplePodcastsHandler Failed, error:{e}")
    finally:
        logger.debug(f"ApplePodcastsHandler Result, next_url:{next_url}, res_list:{res_list}")
        return next_url, res_list


class ApplePod:
    ''' apple podcast类'''
    def __init__(self, url:str, params:dict, resp:dict):
        self.url = url
        self.user_id = self.GetUserId()
        self.params = params
        self.full_url = url+"?"+urlencode(params)
        self.resp = resp

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
        try:
            for data in self.resp["data"]:
                res_list.append(self.ParseApiSingleData(data=data))
            logger.debug(f"ParseApiData Result List: {res_list}")
        except Exception as e:
            logger.error(f"ParseApiData failed, error:{e}")
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
            "title": data["attributes"]["itunesTitle"],
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
                save_path = os.path.join(save_dir, sub_path, file_name) # 存储路径格式:/Podcast_203844864/Podcast_203844864_1000655529212.mp3
                if os.path.exists(save_path):
                    print(f"[Warn] 该路径下{save_path}文件存在，下载跳过")
                    continue
                # 文件下载本地
                succ = download_url_resource_local(url, save_path)
                if not succ:
                    fail_count += 1
                    fail_list.append(url)
                    logger.error(f"DownloadAudio handler failed, url:{url}")
                else:
                    succ_count += 1
                # 上传cos
                cloud_path = "%s/%s/%s"%(cfg["cos_conf"]["save_path"], sub_path, file_name)
                _cloud_link = upload_file(from_path=save_path , to_path=cloud_path) 
                # 移除本地文件
                os.remove(save_path)
                random_sleep(rand_st=20, rand_range=10)
            except Exception as e:
                fail_count += 1
                fail_list.append(url)
                logger.error(f"DownloadAudio failed, error:{e}")
                random_sleep(rand_st=20, rand_range=10)
                continue
                # return False
        else:
            alarm_lark_text(cfg["lark_conf"]["webhook"], f"Apple Podcast DownloadAudio Log \
                \n\tuser_id: {self.user_id} \
                \n\tlink: {self.full_url} \
                \n\tsucc_count: {succ_count} \
                \n\tfail_count: {fail_count} \
                \n\tfail_list: {fail_list}")
        return