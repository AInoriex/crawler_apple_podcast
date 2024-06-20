# -*- coding: utf-8 -*-
import requests

def retry_request_get(url:str, headers=None, verify=True, timeout=10, retry=3)->requests.Response:
    ''' 发送GET请求附带重试次数 '''
    try:
        response = requests.get(url=url, headers=headers, verify=verify, timeout=timeout)
        assert response.status_code == 200
    except Exception as e:
        print(f"retry_request_get failed, retry_count:{retry}", e)
        if retry > 0:
            retry_request_get(url, headers=headers, verify=not(verify), retry=retry-1)
        else:
            raise e
    else:
        return response
