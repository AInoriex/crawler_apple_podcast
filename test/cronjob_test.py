import time
import schedule
from utils.utime import get_now_time_string

COUNT = 0

def cronjob(func, *args, **kwargs):
    ''' 定时器demo 
    @Desc   func作为被调用函数传入cronjob,通过每隔CRON_TIME秒执行一次call_func_with_delay方法,定时器轮询一次时间为GAP_TIME秒
    '''
    CRON_TIME = 10
    GAP_TIME = 5

    print(f"{get_now_time_string()} | schedule registery start")
    # schedule.every(CRON_TIME).seconds.do(call_func_with_delay, func, *args, **kwargs)
    schedule.every(CRON_TIME).seconds.do(func, *args, **kwargs)
    print(f"{get_now_time_string()} | schedule registery end")

    while True:
        print(f"{get_now_time_string()} | schedule.run_pending start")
        schedule.run_pending()
        print(f"{get_now_time_string()} | schedule.run_pending end")
        time.sleep(GAP_TIME)


def call_func_with_delay(func, *args, **kwargs):
    ''' 定时器执行的函数 '''
    print(f"{get_now_time_string()} | call_func_with_delay start")
    ''' do something '''
    func(*args, **kwargs)
    ''' do something '''
    print(f"{get_now_time_string()} | call_func_with_delay end")
    return


def func_test(a:int, b:str):
    ''' 需要调用执行的函数 '''
    global COUNT
    COUNT += 1
    print(f"{get_now_time_string()} | TEST COUNT:{COUNT} Params:{a} {b}")
    

if __name__ == "__main__":
    cronjob(func_test, 1, "2")