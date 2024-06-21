# -*- coding=utf-8
''' ReadME
@Desc       这是腾讯云COS云对象存储服务SDK封装方法, 只要涉及client初始化以及使用client对本地资源的上传下载操作
@Link       产品文档 https://www.tencentcloud.com/zh/document/product/436/6222
@Pip        pip install -U cos-python-sdk-v5
@Author     AInoriex
@Date       2024.05.29
'''

from utils.tool import load_cfg
from utils.logger import init_logger
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import os
from time import sleep

cfg = load_cfg("config.json")
logger = init_logger("cos_sdk")

# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成    
secret_id = cfg["cos_conf"]["secret_id"] # 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
secret_key = cfg["cos_conf"]["secret_key"] # 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
region = 'ap-beijing'      # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
                           # COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
token = None               # 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
scheme = 'https'           # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config, retry=3)
logger.info(
    "cos init client succeed. %s", client.get_conf().get_host(Bucket=cfg["cos_conf"]["bucket"])
)

# 高级上传接口（推荐）
def upload_file(from_path:str, to_path:str)->str:
    '''cos上传接口:根据文件大小自动选择简单上传或分块上传,分块上传具备断点续传功能
    @Params from_path 本地文件路径(exp. ./download/test.mp4)
    @Params to_path 云端存储路径(exp. ./result/test.mp4)
    '''
    if not os.path.exists(from_path):
        logger.error(f"cos upload_file error, not such file {from_path}")
        raise FileNotFoundError
    try:
        response = client.upload_file(
            Bucket=cfg["cos_conf"]["bucket"],
            LocalFilePath=from_path,
            Key=to_path,
            PartSize=1,
            MAXThread=10,
            EnableMD5=False
        )
        cos_link = cfg["cos_conf"]["url_base"] + to_path
        logger.info(f"cos upload_file done, cos_link:{cos_link} local_file_path:{from_path} to_path:{to_path} file_id:{response['ETag']}")
        return cos_link
    except Exception as e:
        logger.error(f"cos upload_file failed, error:{e}")
        raise e

# 高级上传接口（+重试逻辑）
def upload_file_with_retry(from_path:str, to_path:str, retry=3)->str:
    '''cos上传接口:根据文件大小自动选择简单上传或分块上传,分块上传具备断点续传功能
    @Params from_path 本地文件路径(exp. ./download/test.mp4)
    @Params to_path 云端存储路径(exp. ./result/test.mp4)
    '''
    if not os.path.exists(from_path):
        logger.error(f"upload_file_with_retry NO such file {from_path}")
        raise FileNotFoundError
    try:
        response = client.upload_file(
            Bucket=cfg["cos_conf"]["bucket"],
            LocalFilePath=from_path,
            Key=to_path,
            PartSize=10,
            MAXThread=10,
            EnableMD5=False,
        )
        cos_link = cfg["cos_conf"]["url_base"] + to_path
        logger.info(f"upload_file_with_retry upload_file done, cos_link:{cos_link} local_file_path:{from_path} to_path:{to_path} file_id:{response['ETag']}")
    except Exception as e:
        logger.error(f"upload_file_with_retry upload_file failed, retry_count:{retry}, error:{e}")
        if retry > 0:
            sleep(1)
            upload_file_with_retry(from_path=from_path, to_path=to_path, retry=retry-1)
        else:
            raise e
    else:
        return cos_link