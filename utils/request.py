# -*- coding: utf-8 -*-
import requests

def request_get_with_retry(url:str, headers=None, proxies={}, verify=True, timeout=10, stream=False, retry=3)->requests.Response:
    ''' 发送GET请求附带重试次数 
    @Params retry: 重试次数, 默认为3
    @Params others: headers=None, proxies={}, verify=True, timeout=10, stream=False
    '''
    try:
        response = requests.get(url=url, headers=headers, proxies=proxies, verify=verify, stream=stream,timeout=timeout)
        assert response.status_code == 200
    except Exception as e:
        print(f"retry_request_get failed, retry_count:{retry}", e)
        if retry > 0:
            request_get_with_retry(url, 
                headers=headers, proxies=proxies,
                verify=not(verify), stream=stream,
                retry=retry-1
            )
        else:
            raise e
    else:
        return response
