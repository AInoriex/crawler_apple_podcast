# -*- coding: UTF8 -*-
import os
import time
import json
from utils.tool import load_cfg

cfg = load_cfg("config.json")

def get_file_size(filePath):
    ''' 获取文件大小(MB) '''
    fsize = os.path.getsize(filePath)
    return fsize/float(1024*1024)

def save_json_to_file(data_dict:dict)->bool:
    ''' 保存json文件到本地 '''
    output_path = cfg["common"]["output_path"]
    os.makedirs(output_path, exist_ok=True)
    log_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    try:
        with open(f"{output_path}/{log_time}.json", "w", encoding="utf8") as f:
            json.dump(data_dict, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("[ERROR] save_json_to_file failed", e)
        return False
    else:
        return True

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