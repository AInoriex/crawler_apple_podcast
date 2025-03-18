import requests
import os
import json

# class LarkNotice():
#     def __init__(self, notice_text) -> None:
#         self.notice_text = notice_text

def alarm_lark_text(webhook:str, text:str)->bool:
    ''' 飞书普通文本告警 '''
    ''' Expamle Json Send
    {
	    "msg_type": "text",
	    "content": {"text": "test hello world."}
    }'''
    # try to get webhook from global env
    webhook = os.getenv("LARK_WEBHOOK") if webhook == "" else webhook
    if webhook == "":
        print("[utils.lark] webhook is empty, skip alarm to lark.")
        return False
    params = {
	    "msg_type": "text",
	    "content": {"text": f"{text}"}
    }
    print(f"[utils.lark] request: {webhook} | {params}")
    resp = requests.post(url=webhook, json=params)
    # print(f"[utils.lark] response: {resp.status_code} {resp.content}")
    if resp.status_code != 200:
        print(f"[utils.lark] alarm to lark failed, response: {resp.status_code} {resp.content}")
        return False
    resp = resp.json()
    if resp["code"] != 0:
        print(f"[utils.lark] alarm to lark failed, json: {resp}")
        return False
    return True
