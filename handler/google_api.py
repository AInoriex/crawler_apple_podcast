from googlesearch import search
from utils.utime import random_sleep
from utils.logger import init_logger
from db.search_info import SearchInfo
import time

logger = init_logger("google_api")

def Gsearch(search_word:str, start:int, search_total:int, pause:int)->list:
    ''' Google搜索API 
    @Param   search_word:搜索关键字, start:要检索的第一个结果, search_total:搜索结果数量, pause:请求间隔(秒)
    @Date   24.05.23
    @Author xyh
    '''
    # search_total = 20
    # search_word = 'site:https://podcasts.apple.com/us/podcast/'
    # extra_params = {
    #     "oq": "site%3Ahttps%3A%2F%2Fpodcasts.apple.com%2Fus%2Fpodcast%2F"
    # }

    if pause < 1:
        pause = 5
    if search_word == "" or search_total < 0:
        logger.error(f"Gsearch params invalid, search_word:{search_word}, search_total:{search_total}")
        return []

    count = 0
    resList = []
    try:
        for url in search(query=search_word, start=start, stop=search_total, pause=pause):
            count += 1
            logger.debug(f"Gsearch result debug: No.{count} | {url}")
            if url == "":
                logger.warn(f"Gsearch result debug: No.{count} | empty url string")
                continue
            elif not url.startswith("http"):
                logger.warn(f"Gsearch result debug: No.{count} | url invalid")
            resList.append(url)
    except Exception as e:
        logger.error(f"Gsearch Failed, error:{e}")
    else:
        logger.info("Gsearch Succeed.")
    finally:
        return resList


def SaveUrl(batch_id:str, keyword:str, url:str)->bool:
    ''' 单个url检索结果入库 '''
    if url == "":
        logger.error("SaveDb Failed, empty url.")
        return False
    db = SearchInfo(user='root', password='123456', host='127.0.0.1', database='crawler')
    table = "web_search_info"
    user_id = GetApplePodcastUserId(url)
    get_dict = db.Select(table=table, condition=f"result_url = '{url}' or apple_podcast_user_id = '{user_id}'")
    if len(get_dict) > 0:
        logger.warn("SaveDb record existed, skip saving. ID:%s URL:%s USER_ID:%s"%(get_dict[0]['id'], url, user_id))
        return True

    try:
        db.Insert(table=table, values=f"""
            0, '{batch_id}', 'google', '{keyword}', '{url}', '{user_id}', 1, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
        """)
    except Exception as e:
        logger.error(f"SaveDb Insert FAILED, error:{e}")
        return False
    else:
        return True
    finally:
        db.Close()

def SaveUrls(batch_id:str, keyword:str, url_list:list)->bool:
    ''' 单个url检索结果入库 '''
    if len(url_list) <= 0:
        logger.error("SaveDb Failed, empty url list.")
        return False
    db = SearchInfo(user='root', password='123456', host='127.0.0.1', database='crawler')
    table = "web_search_info"

    for url in url_list:
        user_id = GetApplePodcastUserId(url)
        get_dict = db.Select(table=table, condition=f"result_url = '{url}' or apple_podcast_user_id = '{user_id}'")
        if len(get_dict) > 0:
            logger.warn("SaveDb record existed, skip saving. ID:%s URL:%s USER_ID:%s"%(get_dict[0]['id'], url, user_id))
            continue
        try:
            db.Insert(table=table, values=f"""
                0, '{batch_id}', 'google', '{keyword}', '{url}', '{user_id}', 1, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
            """)
        except Exception as e:
            logger.error(f"SaveDb Insert FAILED, url:{url} | error:{e}")
            db.Close()
            return False
        else:
            logger.debug(f"SaveDb Insert Succeed, url:{url}")
            continue
    else:
        db.Close()
        return True


def GetApplePodcastUserId(url:str)->str:
    ''' 获取链接中Apple Podcast的用户id
    \n  exp: https://podcasts.apple.com/us/podcast/oppenheimer/id1220985045 -> 1220985045
    \n  exp: https://podcasts.apple.com/us/podcast/trashfuture/id1261944206 -> 1261944206
    '''
    tmp = url.rsplit("/id")
    user_id = tmp[-1]
    if user_id.isdigit():
        return user_id
    else:
        return ""


# if __name__ == "__main__":
#     Gsearch()