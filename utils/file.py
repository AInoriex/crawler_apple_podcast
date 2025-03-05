# -*- coding: UTF8 -*-

import os
import time
import json
import requests

def get_file_size(filePath):
    ''' 获取文件大小(MB) '''
    fsize = os.path.getsize(filePath)
    return round(fsize / float(1024 * 1024), 2)

def write_json_to_file(json_obj, filename:str):
    ''' json数据写入文件
    @json_obj: 待写入数据
    @out_file: 输出文件
    '''
    with open(filename, "w", encoding="utf8") as f:
        json.dump(json_obj, f, indent=4, ensure_ascii=False)
    print(f"write_json_to_file > 数据已写入文件: {filename}")

def write_string_to_file(text_string:str, filename:str):
    ''' 字符串文本写入文件
    @text_string: 待写入数据
    @out_file: 输出文件
    '''
    with open(filename, "w", encoding="utf8") as f:
        f.write(text_string)
    print(f"write_string_to_file > 数据已写入文件: {filename}")

def add_string_to_file(text_string:str, filename:str):
    ''' 追加字符串文本到文件
    @text_string: 待追加数据
    @out_file: 输出文件
    '''
    with open(filename, "a", encoding="utf8") as f:
        f.write("\n")
        f.write(text_string)
    print(f"add_string_to_file > 数据已追加文件: {filename}")

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
        resp = requests.get(url, headers=headers,proxies=proxies,timeout=(5,20),verify=False)
        if not resp.status_code == 200:
            print(f"download_url_resource_local get url failed. url:{url}")
            return False
        with open(local_path ,mode="wb") as f:
            f.write(resp.content)
    except Exception as e:
        print(f"download_url_resource_local unknown error:{e}")
        return False
    else:
        print(f"download_url_resource_local download succeed. file:{local_path}")
        return True

def remove_file(local_path):
    os.remove(local_path)
    print(f"已删除本地文件: {local_path}")

def read_file(filename:str):
    with open(filename, mode="r", encoding="utf-8") as f:
        res = f.read()
    return res

if __name__ == "__main__":
    url = "https://mcdn.podbean.com/mf/web/3qznfg92me6zs3m4/04-18-Molly-promo-final.mp3"
    save_path = os.path.join(".", "download", "test", "04-18-Molly-promo-final.mp3")
    succ = download_url_resource_local(url=url, local_path=save_path)
    print(f"flag:{succ}")