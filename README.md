# Apple Podcast Crawler

> Author	AInoriex Xiang
> Date	   2024/05/27

## Desc

​	这是Apple播客的音频数据爬取仓库。简要流程如下

1. 从Google搜索引擎获取Apple Podcast用户空间url
2. 遍历url的用户音频获取接口并下载



## Usage

```python
python -m venv .venv
.venv\Script\activate
pip install -r requirements.txt
python main.py google
python main.py podcast
```

