import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from utils.logger import logger
from utils.request import download_resource
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

    # @unittest.skip("暂时跳过 `test_download_resource` 测试")
    def test_download_resource(self):
        self.download_url_list = [
            "https://al-sabeel.net/wp-content/uploads/2024/06/7الفصل_السادس_في_ضبط_مركزية_الإنسان_والدنيا.mp3",
        ]

        succ_count = 0
        fail_count = 0
        for url in self.download_url_list:
            try:
                logger.info(f"当前测试下载URL:{url}")
                with TemporaryDirectory() as tempdir:
                    filename = os.path.join(tempdir, "temp.mp3")

                    # download handler
                    download_resource(url=url, filename=filename, proxies=self.proxies)

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

