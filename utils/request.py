import os
from random import choice, randint, shuffle
from time import sleep
from utils.logger import logger

def get_random_ua():
    """
    Generates a random User-Agent based on a random OS and browser
    
    The random OS can be one of Windows, macOS, or Linux.
    The random browser can be one of safari, firefox, edge (on Windows), or chrome (on Windows or macOS).
    
    Returns a dictionary with three keys: "os", "browser", and "ua", containing the random OS, browser, and User-Agent, respectively.
    """
    from fake_useragent import UserAgent
    os_list = ["Windows", "macOS", "Linux"]
    operate_sys = choice(os_list)
    # print(f"随机os > {operate_sys}")
    browsers_list = ['safari', 'firefox']
    if operate_sys == "Windows":
        browsers_list.append("edge")
    if operate_sys != 'Linux':
        browsers_list.append("chrome")
    br = choice(browsers_list)
    # print(f"随机browser > {br}")
    ua = UserAgent(browsers=[br.lower()], os=[operate_sys.lower()])
    user_agent = ua.random
    # print(f"随机生成的User-Agent: {user_agent}")
    return {
        "os": operate_sys,
        "browser": br,
        "ua": user_agent
    }

def get_random_header():
    ''' 随机生成请求头

    @Example Header
    {
        'sec-ch-ua': '"Firefox";v="99", "Gecko";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"', 
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36', 
        'Accept': 'text/html,application/json;q=0.9,application/x-www-form-urlencoded;q=0.8,application/xml;q=0.8,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Accept-Charset': 'utf-8'
    }
    '''
    from fake_useragent import UserAgent
    ua = UserAgent()

    # 随机选择浏览器类型
    browser_type = choice(['chrome', 'firefox', 'safari', 'edge', 'opera'])

    # 随机选择是移动端还是网页端
    is_mobile = choice([True, False])

    # 随机选择操作系统
    if is_mobile:
        os = choice(['android', 'ios'])
    else:
        # os = choice(['windows', 'macos', 'linux'])
        os = choice(['windows', 'macos'])

    # 随机生成 sec-ch-ua 字段
    if browser_type == 'chrome':
        sec_ch_ua = '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"'
    elif browser_type == 'firefox':
        sec_ch_ua = '"Firefox";v="99", "Gecko";v="99"'
    elif browser_type == 'safari':
        sec_ch_ua = '"Safari";v="99", "WebKit";v="99"'
    elif browser_type == 'edge':
        sec_ch_ua = '"Microsoft Edge";v="99", "Chromium";v="99"'
    else:
        sec_ch_ua = '"Opera";v="99", "Chromium";v="99"'

    # 随机生成 sec-ch-ua-mobile 字段
    sec_ch_ua_mobile = "?1" if is_mobile else "?0"

    # 随机生成 sec-ch-ua-platform 字段
    if os == 'windows':
        sec_ch_ua_platform = '"Windows"'
    elif os == 'macos':
        sec_ch_ua_platform = '"macOS"'
    elif os == 'linux':
        sec_ch_ua_platform = '"Linux"'
    elif os == 'android':
        sec_ch_ua_platform = '"Android"'
    else:
        sec_ch_ua_platform = '"iOS"'

    # 随机生成 User-Agent 字段
    user_agent = ua.random

    # 构造请求头字典
    headers = {
        "sec-ch-ua": sec_ch_ua,
        "sec-ch-ua-mobile": sec_ch_ua_mobile,
        "sec-ch-ua-platform": sec_ch_ua_platform,
        "User-Agent": user_agent,
        "Accept": "text/html,application/json;q=0.9,application/x-www-form-urlencoded;q=0.8,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Accept-Charset": "utf-8",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
    }

    return headers

def download_resource_by_urllib(url:str, filename:str, proxies=None, cookie=None, retry:int=3):
    """
    使用urllib库从url处下载文件到本地的filename

    :param url: 要下载的文件的url
    :param filename: 保存到本地的文件名
    :param proxies: 代理服务器
    :param cookie: cookie
    :return: filename:str, err_msg:str
    """
    from urllib import request, parse
    logger.info(f"download_resource_by_urllib > {url} -- {filename}, retry:{retry}")
    if url == "" or filename == "":
        raise ValueError(f"download_resource url or filename is empty, url:{url}, filename:{filename}")
    encoded_url = parse.quote(url, safe=":/")  # 只保留URL中的协议和路径分隔符
    ua = get_random_header()
    headers = [ (key, value) for key, value in ua.items() ]
    # 添加cookie
    if cookie:
        headers.append(('cookie', cookie))

    def reporthook(block_num, block_size, total_size):
        if block_num // 2 == 0:
            return
        if total_size != -1:
            print(f"\rdownload_resource_by_urllib > {filename}文件大小：{total_size/1048576:.2f}MB | 下载进度：{block_num*block_size/total_size*100:.2f}%", end='')
        
    try:
        # create the object, assign it to a variable
        proxy_handler = request.ProxyHandler(proxies)
        # construct a new opener using your proxy settings
        opener = request.build_opener(proxy_handler)
        opener.addheaders = headers
        # install the openen on the module-level
        request.install_opener(opener)
        request.urlretrieve(encoded_url, filename, reporthook)
        logger.info(f"\ndownload_resource_by_urllib > 文件已下载到：{filename}")
        return filename, ""
    except Exception as e:
        logger.error(f"\ndownload_resource_by_urllib > 下载文件时发生错误：{e}")
        if retry > 0:
            sleep(2)
            return download_resource_by_urllib(url=url, filename=filename, proxies=proxies, cookie=cookie, retry=retry-1)
        # raise e
        return "", f"download_resource_by_urllib error, {e}"

def download_resource_by_ytdlp(url:str, filename:str, proxies=None, cookie=None, retry:int=3):
    """
    使用yt-dlp从url处下载文件到本地的filename

    :param url: 要下载的文件的url
    :param filename: 保存到本地的文件名
    :param proxies: 代理服务器
    :param cookie: cookie
    :return: filename:str, err_msg:str
    """
    import yt_dlp
    from tempfile import TemporaryDirectory
    logger.info(f"download_resource_by_ytdlp > {url} -- {filename}, retry:{retry}")
    try:
        # yt-dlp download options
        ydl_opts = {
            'outtmpl': filename, # 输出文件
            'proxy': proxies,
            'format': 'bestaudio/best', # 音频质量
            'noplaylist': True, # 禁用播放列表
            'postprocessors': [{ 
                'key': 'FFmpegExtractAudio', # 下载音频
                'preferredcodec': 'mp3', # 音频格式
                'preferredquality': '192', # 音频质量
            }],
        }

        # yt-dlp cookies
        with TemporaryDirectory() as tempdir:
            if cookie:
            # cookie值写入临时cookiefile文件
                cookiefile = os.path.join(tempdir, "cookie.txt")
                with open(cookiefile, "w") as f:
                    f.write(cookie)
                ydl_opts['cookiefile'] = cookiefile
        
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            if not os.path.exists(filename):
                raise Exception("download_resource_by_ytdlp 下载文件不存在")
            logger.info(f"\ndownload_resource_by_ytdlp > 文件已下载到：{filename}")
            return filename, ""
    except Exception as e:
        logger.error(f"\ndownload_resource_by_ytdlp > 下载文件时发生错误：{e}")
        if retry > 0:
            sleep(2)
            return download_resource_by_ytdlp(url=url, filename=filename, proxies=proxies, cookie=cookie, retry=retry-1)
        # raise e
        return "", f"download_resource_by_ytdlp error, {e}"
    finally:
        # 清除临时cookiefile文件
        if cookie and os.path.exists(cookiefile):
            os.remove(cookiefile)

# 随机调用download_resource_by_ytdlp, download_resource_by_urllib
def download_resource(url:str, filename:str, proxies=None, cookie=None):
    functions = [download_resource_by_urllib, download_resource_by_ytdlp]
    shuffle(functions)
    for func in functions:
        ret, err_msg = func(url, filename, proxies, cookie)  # 执行函数
        if err_msg != "": 
            logger.error(f"download_resource error, func:{func.__name__}, err_msg:{err_msg}")
            continue
        # 如果err_msg为空，直接返回结果
        return ret

    # 如果所有函数都执行过且err_msg不为空，抛出异常
    raise Exception(f"download_resource error, err_msg:{err_msg}")
