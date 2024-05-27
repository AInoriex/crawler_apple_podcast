from googlesearch import search
# from utils.utime import random_sleep
# from utils.logger import init_logger
from db.search_info import SearchInfo

# logger = init_logger("test_google_search")

def Gsearch(search_word:str, start:int, search_total:int, pause:int)->list:
    ''' Google搜索API 
    @Param   search_word:搜索关键字, start:要检索的第一个结果, search_total:搜索结果数量, pause:请求间隔(秒)
    @Date   24.05.23
    @Author xyh
    '''
    print("Gsearch Start")
    # search_total = 20
    # search_word = 'site:https://podcasts.apple.com/us/podcast/'
    # extra_params = {
    #     "oq": "site%3Ahttps%3A%2F%2Fpodcasts.apple.com%2Fus%2Fpodcast%2F"
    # }

    if pause < 1:
        pause = 5
    if search_word == "" or search_total < 0:
        # logger.error(f"Gsearch params invalid, search_word:{search_word}, search_total:{search_total}")
        return []

    count = 0
    resList = []
    for url in search(query=search_word, start=start, stop=search_total, pause=pause):
        count += 1
        # logger.debug(f"Gsearch result debug: No.{count} | {url}")
        if url == "":
            # logger.warn(f"Gsearch result debug: No.{count} | empty url string")
            continue
        elif not url.startswith("http"):
            # logger.warn(f"Gsearch result debug: No.{count} | url invalid")
            continue
        resList.append(url)
    print("Gsearch End")
    return resList

def SaveDb(batch_id:str, keyword:str, url:str)->bool:
    ''' 检索结果入库 '''
    if url == "":
        # logger.error("SaveDb Failed, empty url.")
        return False
    db = SearchInfo(user='root', password='123456', host='127.0.0.1', database='crawler')
    table = "web_search_info"
    get_dict = db.Select(table=table, condition=f"result_url = '{url}'")
    if len(get_dict) > 0:
        # logger.warn("SaveDb record existed, skip saving. ID:%s URL:%s"%(get_dict[0]['id'], get_dict[0]['result_url']))
        return True

    user_id = GetApplePodcastUserId(url)
    try:
        db.Insert(table=table, values=f"""
            0, '{batch_id}', 'google', '{keyword}', '{url}', '{user_id}', 1, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
        """)
    except Exception as e:
        # logger.error(f"SaveDb Insert FAILED, error:{e}")
        return False
    else:
        return True
    finally:
        db.Close()

def GetApplePodcastUserId(url:str)->str:
    ''' 获取链接中Apple Podcast的用户id
    \n  exp: https://podcasts.apple.com/us/podcast/oppenheimer/id1220985045 -> 1220985045
    '''
    tmp = url.rsplit("/id")
    user_id = tmp[-1]
    if user_id.isdigit():
        return user_id
    else:
        return ""

def func_test():
    ''' 测试try except else finally结构'''
    try:
        print("DEBUG 1")
    except:
        print("DEBUG 2")
        return
    else:
        print("DEBUG 3")
        return
    finally:
        print("DEBUG 4")
        return

if __name__ == "__main__":
    test_batch_id = "TEST_BATCH_240524_01"
    search_word = "site:https://podcasts.apple.com/us/podcast/"

    search_url_list = Gsearch(search_word=search_word, start=0, search_total=3, pause=5)
    print(search_url_list)

    user_id_list = [GetApplePodcastUserId(url) for url in search_url_list]
    print(user_id_list)

    for url in search_url_list:
        SaveDb(batch_id=test_batch_id, keyword=search_word, url=url)
    # func_test()

    print('[DONE]')