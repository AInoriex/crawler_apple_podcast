from utils.utime import get_time_stamp
from utils.exception import *
from requests import get, post
from uuid import uuid4

class CrawlerSearchInfo:
    ''' 检索信息记录表 '''
    def __init__(self):
        self._id = 0
        self._request_id = ""
        self._crawler_id = ""
        self._search_from = ""
        self._search_keyword = ""
        self._result_url = ""
        self._status = 0
        self._create_time = ""
        self._update_time = ""
        pass

    @property
    def request_id(self):   
        return self._request_id
    @property
    def crawler_id(self):   
        return self._crawler_id
    @property
    def result_url(self):   
        return self._result_url

    @property 
    def id(self):   
        return self._id
    # @id.setter 
    # def id(self, v): 
    #     if(v < 0):   
    #         raise ValueError("id value invalid")   
    #     self._id = v
    
    @property
    # get function   
    def status(self):   
        return self._status
    @status.setter 
    # set function   
    def status(self, v): 
        if(v < 0):   
            raise ValueError("status value invalid")   
        self._status = v

    def GetRandomPodcast(self):
        ''' 随机获取一条podcast记录 '''
        url = "https://magicmir.52ttyuyin.com/crawler_api/podcast_get_download_list?sign=%d"%get_time_stamp()
        try:
            print(f"GetRandomPodcast req, url:{url}")
            resp = get(url=url)
            print(f"GetRandomPodcast resp, status_code:{resp.status_code}, content:{resp.content}")
            assert resp.status_code == 200
            resp_json = resp.json()
            print("GetRandomPodcast resp detail, status_code:%d, content:%s"%(resp_json["code"], resp_json["msg"]))
            self.GetPodcast(data=resp_json["data"]["result"][0])
        
        except AssertionError:
            print("GetRandomPodcast assert error, url request failed")
            raise MagicApiException("url request failed")
        except Exception as e:
            print(f"GetRandomPodcast unknown error:{e}")
            raise e
        else:
            print("GetRandomPodcast succeed")
        finally:
            return

    def UpdatePodcastStatus(self):
        ''' 更新Podcast记录 '''
        url = "https://magicmir.52ttyuyin.com/crawler_api/podcast_update_status"
        req = {
            "request_id": str(uuid4()),
            "id": self._id,
            "status": self._status,
        }
        try:
            resp = post(url=url, json=req)
            assert resp.status_code == 200
            resp_json = resp.json()
            print("GetRandomPodcast resp detail, status_code:%d, content:%s"%(resp_json["code"], resp_json["msg"]))
            resp_code = resp_json["code"]
            if resp_code != 0:
                raise MagicApiException(f"UpdatePodcastStatus failed, req:{req}, resp:{resp_json}")
        except Exception as e:
            print(f"UpdatePodcastStatus unknown error:{e}")
            raise e
        else:
            print("UpdatePodcastStatus succeed")

    def GetPodcast(self, data:dict):
        ''' json赋值实例, 结构体如下
        {
            "id": 272,
            "request_id": "TEST_BATCH_240524_04",
            "crawler_id": "659155419",
            "search_from": "google",
            "search_keyword": "site:https://podcasts.apple.com/us/podcast/",
            "result_url": "https://podcasts.apple.com/us/podcast/philosophize-this/id659155419",
            "status": 2,
            "create_time": "2024-05-24T19:34:33+08:00",
            "update_time": "2024-06-06T10:59:22.783219327+08:00"
        }
        '''
        self._id = data["id"]
        self._request_id = data["request_id"]
        self._crawler_id = data["crawler_id"]
        self._search_from = data["search_from"]
        self._search_keyword = data["search_keyword"]
        self._result_url = data["result_url"]
        self._status = data["status"]
        self._create_time = data["create_time"]
        self._update_time = data["update_time"]

if __name__ == "__main__":
    pod = CrawlerSearchInfo()
    pod.GetRandomPodcast()
    print(f"Get Result, id:{pod.id}, crawler_id:{pod.crawler_id}, request_id:{pod.request_id}, status:{pod.status}")

    pod.status = 1
    pod.UpdatePodcastStatus()