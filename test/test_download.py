import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from utils.logger import logger
from utils.request import *
from tempfile import TemporaryDirectory

class TestDownload(unittest.TestCase):
    def setUp(self):
        """测试前置函数，每个测试样例执行前都会调用setUp """
        # 初始化配置
        self.proxies = {
            "http": "http://127.0.0.1:10809",
            "https": "http://127.0.0.1:10809",
        }

        print(f"测试方法 {self._testMethodName} 开始执行")

    @unittest.skip("暂时跳过 `test_download_resource_by_urllib` 测试")
    def test_download_resource_by_urllib(self):
        self.download_url_list = [
            "https://al-sabeel.net/wp-content/uploads/2024/06/7الفصل_السادس_في_ضبط_مركزية_الإنسان_والدنيا.mp3",
            # "https://sphinx.acast.com/p/open/s/6168a08788593900146910ea/e/https%3A%2F%2Fapi.spreaker.com%2Fepisode%2F43254847/media.mp3", # FAILED: 跳转链接+签名
        ]

        succ_count = 0
        fail_count = 0
        for url in self.download_url_list:
            try:
                logger.info(f"当前测试下载URL:{url}")
                with TemporaryDirectory() as tempdir:
                    filename = os.path.join(tempdir, "temp.mp3")

                    # download handler
                    download_resource_by_urllib(url=url, filename=filename, proxies=self.proxies, cookie=None)

                    self.assertTrue(os.path.exists(filename))
                    self.assertGreater(os.path.getsize(filename), 0)

                    os.remove(filename)
            except Exception as e:
                fail_count += 1
                logger.error(f"[!] 链接{url} 测试下载失败，error:{e}")
            else:
                succ_count += 1
                logger.info(f"链接{url} 测试下载通过")
        logger.info(f"最终测试结果，成功：{succ_count}条， 失败：{fail_count}条")

    @unittest.skip("暂时跳过 `test_yt_dlp_download` 测试")
    def test_yt_dlp_download(self):
        import yt_dlp
        self.download_url_list = [
            "https://sphinx.acast.com/p/open/s/6168a08788593900146910ea/e/https%3A%2F%2Fapi.spreaker.com%2Fepisode%2F43254847/media.mp3", # PASS: 跳转链接+签名
        ]

        succ_count, fail_count = int(0), int(0)
        for url in self.download_url_list:
            try:
                logger.info(f"当前测试下载URL:{url}")
                with TemporaryDirectory() as tempdir:
                    filename = os.path.join(tempdir, "temp.mp3")

                    # download handler
                    ydl_opts = {
                        'outtmpl': filename, # 输出文件
                        'format': 'bestaudio/best', # 音频质量
                        'noplaylist': True, # 禁用播放列表
                        'postprocessors': [{ 
                            'key': 'FFmpegExtractAudio', # 下载音频
                            'preferredcodec': 'mp3', # 音频格式
                            'preferredquality': '192', # 音频质量
                        }],
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])

                    self.assertTrue(os.path.exists(filename))
                    self.assertGreater(os.path.getsize(filename), 0)

                    os.remove(filename)
            except Exception as e:
                fail_count += 1
                logger.error(f"[!] 链接{url} 测试下载失败，error:{e}")
            else:
                succ_count += 1
                logger.info(f"链接{url} 测试下载通过")
        logger.info(f"最终测试结果，成功：{succ_count}条， 失败：{fail_count}条")

    # @unittest.skip("暂时跳过 `test_download_resource` 测试")
    def test_download_resource(self):
        self.download_url_list = [
            "https://sphinx.acast.com/p/open/s/6168a08788593900146910ea/e/https%3A%2F%2Fapi.spreaker.com%2Fepisode%2F43254847/media.mp3", # FAILED: 跳转链接+签名
        ]

        succ_count, fail_count = int(0), int(0)
        for url in self.download_url_list:
            try:
                logger.info(f"当前测试下载URL:{url}")
                with TemporaryDirectory() as tempdir:
                    filename = os.path.join(tempdir, "this_is_a_test_file.mp3")

                    # download handler
                    filename = download_resource(url=url, filename=filename)

                    self.assertTrue(os.path.exists(filename))
                    self.assertGreater(os.path.getsize(filename), 0)

                    os.remove(filename)
            except Exception as e:
                fail_count += 1
                logger.error(f"[!] 链接{url} 测试下载失败，error:{e}")
            else:
                succ_count += 1
                logger.info(f"链接{url} 测试下载通过")
        logger.info(f"最终测试结果，成功：{succ_count}条， 失败：{fail_count}条")

if __name__ == "__main__":
    unittest.main()

