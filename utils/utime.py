# -*- coding: UTF8 -*-
import time
import random

FORMATDAYTIMESTRING = "%Y-%m-%d %H:%M:%S"
FORMATDAYTIMESTRING_SHORT = "%Y%m%d%H%M%S"
FORMATDAYSTRING = "%Y-%m-%d"
FORMATDAYSTRING_SHORT = "%Y%m%d"

def random_sleep(rand_range:int, rand_st:int) -> None:
    '''随机等待[rand_st, rand_st+rand_range]秒'''
    if rand_range < 1:
        rand_range = 5
    if rand_st < 1:
        rand_st = 5
    rand_range = random.randint(rand_st, rand_st + rand_range)
    print(f"random_sleep {rand_range} seconds")
    time.sleep(rand_range)
    return

def get_now_time_string() -> str:
    ''' 返回当前日期时间字符串，格式：%年-%月-%日 %时:%分:%秒 '''
    return time.strftime(FORMATDAYTIMESTRING, time.localtime())

def get_now_time_string_short() -> str:
    ''' 返回当前日期时间字符串，格式：%年%月%日%时%分%秒 '''
    return time.strftime(FORMATDAYTIMESTRING_SHORT, time.localtime())

def get_now_day_string() -> str:
    ''' 返回当前日期字符串，格式：%年-%月-%日'''
    return time.strftime(FORMATDAYSTRING, time.localtime())

def get_now_day_string_short() -> str:
    ''' 返回当前日期字符串，格式：%年%月%日 '''
    return time.strftime(FORMATDAYSTRING_SHORT, time.localtime())

def get_time_stamp() -> int:
    ''' 获取时间戳 '''
    return int(time.time())

def format_second_to_time_string(sec=0.0) -> str:
    ''' 转化秒数为时间字符串 '''
    if sec < 60:
        return f"{sec:.2f}秒"
    elif sec < 3600:
        minutes = int(sec // 60)
        seconds = sec % 60
        return f"{minutes}分钟{seconds:.2f}秒" if seconds > 0 else f"{minutes}分钟"
    else:
        hours = int(sec // 3600)
        minutes = int((sec % 3600) // 60)
        seconds = sec % 60
        time_str = f"{hours}小时"
        if minutes > 0:
            time_str += f"{minutes}分钟"
        if seconds > 0:
            time_str += f"{seconds:.2f}秒"
        return time_str

def timestamp_to_time(timestamp:int) -> str:
    """ 时间戳转化为时间 """
    return time.strftime(FORMATDAYTIMESTRING, time.localtime(timestamp))
