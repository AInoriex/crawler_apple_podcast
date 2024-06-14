# -*- coding: UTF8 -*-
import os
import time
import json
import requests
from utils.tool import load_cfg
from traceback import format_exception # Python 3.10+
from tqdm import tqdm

cfg = load_cfg("config.json")

def get_file_size(filePath):
    ''' 获取文件大小(MB) '''
    fsize = os.path.getsize(filePath)
    return fsize/float(1024*1024)

def save_json_to_file(data_dict:dict, save_path="")->bool:
    ''' 保存json文件到本地 '''
    if save_path == "":
        output_path = cfg["common"]["output_path"]
        os.makedirs(output_path, exist_ok=True)
        log_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
        save_path = f"{output_path}/{log_time}.json"
    try:
        with open(save_path, "w", encoding="utf8") as f:
            json.dump(data_dict, f, indent=4, ensure_ascii=False)
    except Exception as e:
        err = "".join(format_exception(e)).strip()
        print("[ERROR] save_json_to_file failed", e)
        return False
    else:
        return True

def get_json_from_file(path:str):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf8") as f:
            result = json.load(fp=f)
    except Exception as e:
        err = "".join(format_exception(e)).strip()
        print("[ERROR] get_json_from_file failed", err)
        return None
    else:
        return result

# def save_any_to_file()->bool:
#     ''' 保存任意数据到本地 '''
#     output_path = cfg["common"]["output_path"]
#     os.makedirs(output_path, exist_ok=True)
#     log_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
#     try:
#         with open(f"{output_path}/{log_time}_raw.txt", "w", encoding="utf8") as f:
#             json.dump(data_dict, f, indent=4, ensure_ascii=False)
#     except Exception as e:
#         print("[ERROR] save_json_to_file failed", e)
#         return False
#     else:
#         return True

def download_url_resource_local(url:str, local_path:str)->bool:
    ''' 下载url资源到本地 '''
    base = os.path.dirname(local_path)
    os.makedirs(base, exist_ok=True)

    if url == "" or not url.startswith("http"):
        print(f"[Warn] url无效，下载跳过; url:{url}")
        return False
    if os.path.exists(local_path):
        print(f"[Warn] 该路径下{local_path}文件存在，下载跳过")
        return True

    headers={}
    proxies={}
    try:
        resp = requests.get(url, headers=headers,proxies=proxies,timeout=(5,20),verify=False, stream=True)
        if not resp.status_code == 200:
            print(f"download_url_resource_local get url failed. url:{url}")
            return False
        # with open(local_path ,mode="wb") as f:
        #     f.write(resp.content)
        total_bytes = resp.headers.get('content-length', 0) # 获取文件的总大小
        total_size = int(total_bytes)/1024
        print("[DEBUG] 当前下载文件大小 %.2f MB"%(total_size))
        total_size = int(total_bytes)*100/1024
        with open(local_path, mode="wb") as f:
            for data in tqdm(resp.iter_content(chunk_size=1024*10), total=total_size, unit='KB', unit_scale=True, desc="Download File", unit_divisor=1024):
                f.write(data)
    except Exception as e:
        print(f"download_url_resource_local unknown error:{e}")
        return False
    else:
        print(f"download_url_resource_local download succeed. file:{local_path}")
        return True

if __name__ == "__main__":
    # url = "https://mcdn.podbean.com/mf/web/3qznfg92me6zs3m4/04-18-Molly-promo-final.mp3"
    # save_path = os.path.join(".", "download", "test", "04-18-Molly-promo-final.mp3")
    # succ = download_url_resource_local(url=url, local_path=save_path)
    # print(f"flag:{succ}")
    result = get_json_from_file(path="F:\\github_repo\\AInoriex-crawler_apple_podcast\\output\\apple_podcast\\Podcast_1622218223.json")
    print(result)