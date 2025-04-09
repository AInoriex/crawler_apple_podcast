'''
@Author     AInoriex
@Date       25.03.06
@Desc       用于解析并采集单音频页面的音频数据
'''

import json
from lxml import etree
import random
import re
import requests
from utils.logger import logger
from db.crawler_plugin import VideoMeta, generate_meta_id
from utils.utime import random_sleep

def get_apple_podcast_audio_id(url):
    """
    获取播客音频id
    https://podcasts.apple.com/us/podcast/{audio_name}/id{episode_id}?i={audio_id}&params=xxx -> audio_id
    """
    audio_id = url.split("&")[0].split("?i=")[-1]
    return audio_id

def apple_podcast_plugin_handler(url):
    """
    单条音频播客解析
    @Param  url: str, 播客音频url，格式要求：https://podcasts.apple.com/us/podcast/{audio_name}/id{episode_id}?i={audio_id}
    @Return VideoMeta, 音频信息
    """
    # 可用函数列表
    functions = [apple_podcast_plugin_handler_web, apple_podcast_plugin_handler_api, apple_podcast_plugin_handler_api_with_login]
    random.shuffle(functions)  # 随机执行

    for func in functions:
        ret, err_msg = func(url)  # 执行函数
        if err_msg != "": 
            logger.error(f"apple_podcast_plugin_handler error, func:{func.__name__}, err_msg:{err_msg}")
            random_sleep(1, 3)
            continue
        # 如果err_msg为空，直接返回结果
        return ret

    # 如果所有函数都执行过且err_msg不为空，抛出异常
    raise Exception(f"apple_podcast_plugin_handler error, err_msg:{err_msg}")

'''
@ExampleParam.url  https://podcasts.apple.com/us/podcast/2281-elon-musk/id360084272?i=1000696846801
@ExampleParam.url  https://podcasts.apple.com/us/podcast/the-persian-wars-xerxes-thermopylae-and-salamis/id1520403988?i=1000695929043
'''

def apple_podcast_plugin_handler_web(url:str)->tuple[VideoMeta, str]:
    """
    基于html源码解析获取mp3信息
    """
    def extract_audio_link(html_content):
        ''' 提取音频链接 '''
        html_text = etree.tostring(etree.HTML(html_content), method="text", encoding="unicode")
        # 正则匹配 https://xxx/xxx.mp3 或者 https://xxx/xxx.mp3?xxx=xxx
        pattern = re.compile(r'(https://[^"]+\.mp3\?[^"]*)')
        mp3_links = re.findall(pattern, html_text)
        if len(mp3_links) > 0:
            return mp3_links[0]
        pattern = re.compile(r'(https://[^"]+\.mp3)')
        mp3_links = re.findall(pattern, html_text)
        if len(mp3_links) > 0:
            return mp3_links[0]
        raise KeyError("正则匹配mp3链接失败")

    def format_duration_string_to_int(duration_str):
        """
        将 ISO 8601 时间持续期字符串（如 PT1H8M15S）转换为总秒数。
        
        参数:
            duration_str (str): ISO 8601 时间持续期字符串，例如 'PT1H8M15S'
        
        返回:
            int: 总秒数
        """
        try:
            # 定义正则表达式，匹配时间单位和对应的数值
            pattern = r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
            # 使用正则表达式解析字符串
            match = re.match(pattern, duration_str)
            if not match:
                raise ValueError("无效的时间持续期格式")
            # 提取各时间单位的数值，如果没有对应单位则为 0
            days, hours, minutes, seconds = match.groups(default=0)
            days, hours, minutes, seconds = int(days), int(hours), int(minutes), int(seconds)
            # 计算总秒数
            total_seconds = (days * 24 * 60 * 60) + (hours * 60 * 60) + (minutes * 60) + seconds
            return total_seconds
        except Exception as e:
            logger.error(f"apple_podcast_plugin_handler_web format_duration_string_to_int failed, duration_str:{duration_str}, error:{e}")
            return 0

    def extract_audio_meta(html_content, obj:VideoMeta):
        ''' 提取音频meta信息 '''
        elements = etree.HTML(html_content).xpath('//script[@id="schema:episode"]/text()')
        if len(elements) <= 0:
            raise KeyError("提取mp3.meta信息失败")

        # 解析JSON
        try:
            text = elements[0].strip()
            json_data = json.loads(text)
            # print(json_data)
            obj.title = json_data.get('name', '')
            obj.description = json_data.get('description', '')
            # obj.source_url = json_data.get('url', '')
            obj.source_url = url
            obj.duration_string = json_data.get('duration', '')
            obj.duration = round(format_duration_string_to_int(obj.duration_string)) if obj.duration_string != "" else 0
            obj.categories = json_data.get('genre', [])
            obj.channel = json_data.get('productionCompany', '')
            obj.uploader = json_data.get('partOfSeries').get('name', '')
            obj.uploader_url = json_data.get('partOfSeries').get('url', '')
            obj.upload_date = json_data.get('datePublished', '')
        except Exception as e:
            logger.error(f"apple_podcast_plugin_handler_web extract_audio_meta failed, error:{e}")
        finally:
            return obj
        
    try:
        # 获取请求参数:音频id
        audio_id = get_apple_podcast_audio_id(url)
        if audio_id == "":
            raise ValueError("get empty audio_id")

        v = VideoMeta(
            video_id=generate_meta_id(audio_id),
            type="音频",
            is_success=1,
            storage_location="",
        )

        # 发起请求获取网页内容
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        # print(response.text)
        # html_content = response.text
        html_content = response.content.decode('utf-8')

        # 提取音频链接
        v.download_url = extract_audio_link(html_content)

        # 提取音频meta信息
        v = extract_audio_meta(html_content, v)

        return v, str("")

    except requests.RequestException as e: # 请求失败
        err_msg = str(f"apple_podcast_plugin_handler_web请求失败, {e}")
        logger.error(f"{err_msg}, url:{url}, response.text:{response.text}")
        return None, err_msg
    except KeyError as e: # 正则匹配失败
        err_msg = str(f"apple_podcast_plugin_handler_web匹配失败, 未能正确解析MP3信息, error:{e}")
        logger.error(f"{err_msg}, error:{e}, url:{url}, html:{html_content}")
        return None, err_msg
    except Exception as e:
        err_msg = str(f"apple_podcast_plugin_handler_web未知错误, error:{e}")
        logger.error(f"{err_msg}, url:{url}, error:{e}")
        return None, err_msg

def apple_podcast_plugin_handler_api(url:str)->tuple[VideoMeta, str]:
    """
    调播客后台API获取mp3信息
    """
    def extract_audio_link(json_data):
        ''' 提取音频链接 '''
        attributes = json_data.get("attributes")
        return attributes.get("assetUrl", "")

    def extract_audio_meta(json_data, obj:VideoMeta):
        ''' 提取音频meta信息 '''
        logger.debug("apple_podcast_plugin_handler_api extract_audio_meta json_data", json_data)
        # 解析JSON
        try:
            attributes = json_data.get("attributes")
            obj.title = attributes.get('name', '')
            obj.description = attributes.get('description').get('standard', '')
            # obj.source_url = attributes.get('url', '')
            obj.source_url = url
            obj.duration_string = str(attributes.get('durationInMilliseconds', ''))
            obj.duration = round(int(obj.duration_string)/1000) if obj.duration_string != "" else 0
            obj.categories = attributes.get('genreNames', [])
            obj.channel = attributes.get('artistName', '')
            obj.uploader = attributes.get('artistName', '')
            obj.uploader_url = attributes.get('websiteUrl')
            obj.upload_date = attributes.get('releaseDateTime', '')
        except Exception as e:
            logger.error(f"apple_podcast_plugin_handler_api extract_audio_meta failed, error:{e}")
        finally:
            return obj

    try:
        # 获取请求参数:音频id
        audio_id = get_apple_podcast_audio_id(url)
        if audio_id == "":
            raise ValueError("get empty audio_id")
        
        v = VideoMeta(
            video_id=generate_meta_id(audio_id),
            type="音频",
            is_success=1,
            storage_location="",
        )

        # 请求API
        request_api = "https://amp-api.podcasts.apple.com/v1/catalog/us/podcast-episodes"
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "authorization": "Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkRBSlcxUk8wNjIifQ.eyJpc3MiOiJFUk1UQTBBQjZNIiwiaWF0IjoxNzM3Mzc4NTYxLCJleHAiOjE3NDM1OTkzNjEsInJvb3RfaHR0cHNfb3JpZ2luIjpbImFwcGxlLmNvbSJdfQ._ZKKySf4sIEzvRY7XQGQj5zo-8xtzcXB3I5Zw8vZTaBajf1VjFIqlOqKmgIQwCd7dYVy7HnNoNQQ9RwTWgztSg",
            "cache-control": "no-cache",
            "origin": "https://embed.podcasts.apple.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://embed.podcasts.apple.com/",
            "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Microsoft Edge\";v=\"133\", \"Chromium\";v=\"133\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
        }
        params = {
            "ids": audio_id
        }
        logger.info(f"apple_podcast_plugin_handler_api request, url:{request_api}, headers:{headers}, params:{params}")
        response = requests.get(request_api, headers=headers, params=params)
        if response.status_code != 200:
            raise requests.RequestException(f"request failed, {response.status_code}")
        json_data = response.json()
        if len(json_data.get("data", [])) <= 0:
            raise requests.RequestException(f"response get empty data")
        json_data = json_data['data'][0]

        # 提取音频链接
        v.download_url = extract_audio_link(json_data)

        # 提取音频meta信息
        v = extract_audio_meta(json_data, v)

        return v, str("")

    except ValueError as e: # get_apple_podcast_audio_id
        err_msg = str(f"apple_podcast_plugin_handler_api预处理失败, {e}")
        logger.error(f"{err_msg}, url:{url}")
        return None, err_msg
    except requests.RequestException as e: # 请求失败
        err_msg = str(f"apple_podcast_plugin_handler_api请求失败, {e}")
        logger.error(f"{err_msg}, url:{url}, params:{params}, headers:{headers}, response.text:{response.text}")
        return None, err_msg
    except KeyError as e: # json解析失败
        err_msg = str(f"apple_podcast_plugin_handler_api失败, 未能正确解析MP3信息, response.json:{response.json()}, error:{e}")
        logger.error(f"{err_msg}, error:{e}, url:{url}, response.json:{response.json()}")
        return None, err_msg
    except Exception as e:
        err_msg = str(f"apple_podcast_plugin_handler_api未知错误, error:{e}")
        logger.error(f"{err_msg}, url:{url}, error:{e}")
        return None, err_msg

def apple_podcast_plugin_handler_api_with_login(url:str)->tuple[VideoMeta, str]:
    """
    调播客后台API获取mp3信息，需要登录Apple账号
    """
    def extract_audio_link(json_data):
        ''' 提取音频链接 '''
        attributes = json_data.get("attributes")
        return attributes.get("assetUrl", "")

    def extract_audio_meta(json_data, obj:VideoMeta):
        ''' 提取音频meta信息 '''
        logger.debug("apple_podcast_plugin_handler_api_with_login extract_audio_meta json_data", json_data)
        # 解析JSON
        try:
            attributes = json_data.get("attributes")
            obj.title = attributes.get('name', '')
            obj.description = attributes.get('description').get('standard', '')
            # obj.source_url = attributes.get('url', '')
            obj.source_url = url
            obj.duration_string = str(attributes.get('durationInMilliseconds', ''))
            obj.duration = round(int(obj.duration_string)/1000) if obj.duration_string != "" else 0
            obj.categories = attributes.get('genreNames', [])
            obj.channel = attributes.get('artistName', '')
            obj.uploader = attributes.get('artistName', '')
            obj.uploader_url = attributes.get('websiteUrl')
            obj.upload_date = attributes.get('releaseDateTime', '')
        except Exception as e:
            logger.error(f"apple_podcast_plugin_handler_api_with_login extract_audio_meta failed, error:{e}")
        finally:
            return obj

    try:
        # 获取请求参数:音频id
        audio_id = get_apple_podcast_audio_id(url)
        if audio_id == "":
            raise ValueError("get empty audio_id")
        
        v = VideoMeta(
            video_id=generate_meta_id(audio_id),
            type="音频",
            is_success=1,
            storage_location="",
        )

        # 请求API
        # request_api = f"https://amp-api.podcasts.apple.com/v1/catalog/us/podcast-episodes"
        request_api = f"https://amp-api.podcasts.apple.com/v1/catalog/us/podcast-episodes/{audio_id}"
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "authorization": "Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkM0SjdHQlA3NEgifQ.eyJpc3MiOiJVTTdOOVJUVDdHIiwiaWF0IjoxNzQyMjQyNTMwLCJleHAiOjE3NDk1MDAxMzAsInJvb3RfaHR0cHNfb3JpZ2luIjpbImFwcGxlLmNvbSJdfQ.MDB9unxGCOXz0GgmhNidPj1rw8gjfog82fwWPUoMKXkL8bFHv1-VUk0yp5GLlgukWrw8i2gtJSUyczet9PqQHA",
            "cache-control": "no-cache",
            "media-user-token": "AphTXfnKj/EQTQGGXNMeXaY5lqLrJwX9Lm5hAlXkE0pt6MczC8PNCwAVW5LESQsbSphel3xb0Au7ePjGw2rP9rOZVxB5t2jbltU5GmjilIkbmJTjZYoumtJUZtazMzCI5+4c4iVS5jadpAFV5QEQS6PmaFO6Z/kH5SchFArnr/1tLE0Qj0sHzpD2KAXrbd61mxxb/B+HzIDcextosy+UmMelPgLQ9jDbVTwU3I2dJFFchFXUdQ==",
            "origin": "https://podcasts.apple.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://podcasts.apple.com/",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
        }
        params = {
            "extend": "isSubscribed,personalizedSubscriptionOffers",
            "extend[podcast-channels]": "editorialArtwork,subscriptionArtwork,subscriptionBrandLogoArtwork",
            "include": "channel,playback-position",
            "include[podcast-channels]": "podcasts",
            "limit[podcasts]": "10",
            "extend[podcast-episodes]": "inLibrary",
            "with": "appOffers,entitlements",
            # "l": "zh-Hans-CN"
        }
        logger.info(f"apple_podcast_plugin_handler_api_with_login request, url:{request_api}, headers:{headers}, params:{params}")
        response = requests.get(request_api, headers=headers, params=params)
        if response.status_code != 200:
            raise requests.RequestException(f"request failed, {response.status_code}")
        json_data = response.json()
        if len(json_data.get("data", [])) <= 0:
            raise requests.RequestException(f"response get empty data")
        json_data = json_data['data'][0]

        # 提取音频链接
        v.download_url = extract_audio_link(json_data)

        # 提取音频meta信息
        v = extract_audio_meta(json_data, v)

        return v, str("")

    except ValueError as e: # get_apple_podcast_audio_id
        err_msg = str(f"apple_podcast_plugin_handler_api_with_login 预处理失败, {e}")
        logger.error(f"{err_msg}, url:{url}")
        return None, err_msg
    except requests.RequestException as e: # 请求失败
        err_msg = str(f"apple_podcast_plugin_handler_api_with_login 请求失败, {e}")
        logger.error(f"{err_msg}, url:{url}, params:{params}, headers:{headers}, response.text:{response.text}")
        return None, err_msg
    except KeyError as e: # json解析失败
        err_msg = str(f"apple_podcast_plugin_handler_api_with_login 失败, 未能正确解析MP3信息, response.json:{response.json()}, error:{e}")
        logger.error(f"{err_msg}, error:{e}, url:{url}, response.json:{response.json()}")
        return None, err_msg
    except Exception as e:
        err_msg = str(f"apple_podcast_plugin_handler_api_with_login 未知错误, error:{e}")
        logger.error(f"{err_msg}, url:{url}, error:{e}")
        return None, err_msg

if __name__ == "__main__":
    test_url = "https://podcasts.apple.com/us/podcast/2281-elon-musk/id360084272?i=1000696846801"
    # mp3_links, err_msg = str(apple_podcast_plugin_handler_web(test_url)
    # mp3_links, err_msg = str(apple_podcast_plugin_handler_api(test_url)
    obj, err_msg = str(apple_podcast_plugin_handler(test_url))
    print("提取到的MP3链接:", obj)
    print("Error:", err_msg)