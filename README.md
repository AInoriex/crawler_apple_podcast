# Apple Podcast Crawler

> Author	AInoriex
> Date	   2025/03/07

## 概述

​	这是Apple播客的音频数据爬取仓库。用于解析采集播客音频数据。项目目前分两种模式启动。



### main.py

​	代码简要流程如下：

1. 从Google搜索引擎获取Apple Podcast用户空间url
2. 遍历url的用户音频获取接口并下载



### *main_plugin.py

​	这是兼容数据中台的插件服务，用于系统化管理多进程采集任务并对每个进程上报进程状态。

​	对于每个采集进程大致流程如下：

1. 创建心跳上报线程定时上报状态信息
2. 轮询获取采集任务接口获取待处理任务
3. 解析任务目标url页面信息
4. 下载音频到本地并上传obs
5. 回调任务结果



## 使用方法

### 初始化环境

```
python -m venv .venv
.venv\Script\activate
pip install -r requirements.txt
```

### 修改配置文件

```
.env
./conf/config.json
./conf/config.ini
```

### 运行

```python
python main.py google
python main.py podcast
# OR
python main_plugin.py
```
