import requests
from utils.logger import init_logger
from  utils import user_agent
import json
import random

logger = init_logger("apple_podcast_api")

def ApplePodcastsHandler(url:str, params:dict):
    ''' 获取&存储 Apple's Podcast 音频数据 '''
    logger.debug(f"ApplePodcastsHandler params, url:{url}, params:{params}")
    if url == "":
        logger.error("ApplePodcastsHandler params invalid, empty url")
        return
    # url = "https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/1261944206/episodes"
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
        "Authorization": "Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkNSRjVITkJHUFEifQ.eyJpc3MiOiI4Q1UyNk1LTFM0IiwiaWF0IjoxNzEzMzY5MDc0LCJleHAiOjE3MjA2MjY2NzQsInJvb3RfaHR0cHNfb3JpZ2luIjpbImFwcGxlLmNvbSJdfQ.n3Qn-2LZW7iy-X79yHU7f41K05iTBuN3ycm_Bqp_nqHpaMyLKCG-zpiuBkVExYMj7YtJShSIxaFLJTvFB6vATA"
    }

    logger.debug(f"ApplePodcastsHandler Request: {url} | {params} | {headers}")
    response = requests.get(url, headers=headers, params=params, verify=True)
    # logger.debug(f"ApplePodcastsHandler Response: {response.status_code} | {response.content}")
    # if response.status_code != 200:
    #     logger.error(f"ApplePodcastsHandler request failed, response:{response.status_code} | {response.content}")
    #     return "", []
    assert response.status_code == 200
    resp = response.json()

    applePod = ApplePod(url, resp)
    next_url = applePod.GetNextUrl()
    res_list = applePod.ParseApiData()

    if not next_url.startswith("http"):
        next_url = "https://amp-api.podcasts.apple.com" + next_url
    logger.debug(f"ApplePodcastsHandler Result, next_url:{next_url}, res_list:{res_list}")
    return next_url, res_list


class ApplePod:
    ''' apple podcast 存储结构'''
    def __init__(self, url:str, resp:dict):
        self.url = url
        self.user_id = self.GetUserId()
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
        ''' 解析响应体data字段 '''
        # logger.debug(f"GetNextUrl Param, {self.resp}")
        if "data" not in self.resp.keys():
            logger.error("ParseApiData failed, no such `data` key in response.")
            return []
        res_list = []
        len_data = len(self.resp["data"])
        logger.info(f"ParseApiData 共获取到{len_data}条数据")
        # for data in self.resp["data"]:
        for data in self.resp["data"]:
            res_list.append(self.ParseApiSingleData(data=data))
        logger.debug(f"ParseApiData Result List: {res_list}")
        return res_list


    def ParseApiSingleData(self, data:dict)->dict:
        ''' 解析单个data数据'''
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