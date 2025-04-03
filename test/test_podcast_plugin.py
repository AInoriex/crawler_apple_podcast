import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import unittest
import time
from crawler_plugin import apple_podcast_crawler_plugin

class TestApplePodcastCrawlerPlugin(unittest.TestCase):
    def setUp(self):
        """测试前置函数，每个测试样例执行前都会调用setUp """
        # 初始化配置
        self.worker_id = f"selftest_{int(time.time())}"
        self.server_name = "local_computer_test"
        
        print(f"测试方法 {self._testMethodName} 开始执行")

    @unittest.skip("暂时跳过 `test_example_task` 测试")
    def test_example_task(self):
        task_data = { 'type': '', 'owner': 'test_owner', 'publisher': 'TBS RADIO', 'p_id': '1532201544', 'source': 'apple_podcast', 'label': [''], 'source_url': 'https://podcasts.apple.com/us/podcast/gedanken-zu-weihnachten-petra-sedlbauer/id1679897972?i=1000648197502&l=zh-Hans-CN', 'encoding': '', "storage_location": "/multimodel.db/apple_podcast/", 'security': '', 'resolution': 0}
        result = apple_podcast_crawler_plugin(url=task_data["source_url"], other_data=task_data, worker_id=self.worker_id, server_name=self.server_name)
        self.assertTrue(result)

    @unittest.skip("暂时跳过 `test_prod_task_1` 测试")
    def test_prod_task_1(self):
        ''' 测试线上失败任务1
        @报错原因：'ascii' codec can't encode characters in position 33-37: ordinal not in range(128) 
        @报错日期：2025年4月2日 18:26
        '''
        task_data = {'type': '', 'owner': '', 'publisher': '', 'p_id': '1564116462', 'source': 'apple_podcast', 'label': [''], 'source_url': 'https://podcasts.apple.com/ma/podcast/%D9%83%D8%AA%D8%A7%D8%A8-%D8%B5%D9%88%D8%AA%D9%8A-%D8%A7%D9%84%D8%B9%D9%82%D8%A7%D8%A6%D8%AF%D9%8A%D8%A9-%D8%A7%D9%84%D9%82%D8%A7%D8%B5%D8%B1%D8%A9-7-8-%D8%A7%D9%84%D9%81%D8%B5%D9%84-%D8%A7%D9%84%D8%B3%D8%A7%D8%AF%D8%B3/id1564116462?i=1000660740012', 'encoding': '', 'storage_location': 'obs://obs-prod-hw-bj-bdt-multimodel/multimodel.db/apple_podcast_multilingual_video', 'metadata_location': 'cosn://cos-prod-tc-bj-bdt-delta-1302248489/multimodel.db/youtube_multilingual_video', 'security': '', 'resolution': 0}
        result = apple_podcast_crawler_plugin(url=task_data["source_url"], other_data=task_data, worker_id=self.worker_id, server_name=self.server_name)
        self.assertTrue(result)
    
    @unittest.skip("暂时跳过 `test_prod_task_2` 测试")
    def test_prod_task_2(self):
        ''' 测试线上失败任务2
        @报错原因：apple_podcast_plugin_handler error, apple_podcast_plugin_handler_api请求失败, request failed, 401 
        @报错日期：2025年4月3日 15:24
        '''
        task_data = {'type': '', 'owner': '', 'publisher': 'thebookvoice.com', 'p_id': '1805998074', 'source': 'apple_podcast', 'label': [''], 'source_url': 'https://podcasts.apple.com/ma/podcast/spanish-ukus-by-renato-g%C3%B3mez-herrera/id1805998074?i=1000701831828', 'encoding': '', 'storage_location': 'obs://obs-prod-hw-bj-bdt-multimodel/multimodel.db/apple_podcast_multilingual_video', 'metadata_location': 'cosn://cos-prod-tc-bj-bdt-delta-1302248489/multimodel.db/youtube_multilingual_video', 'security': '', 'resolution': 0}
        result = apple_podcast_crawler_plugin(url=task_data["source_url"], other_data=task_data, worker_id=self.worker_id, server_name=self.server_name)
        self.assertTrue(result)
    
    @unittest.skip("暂时跳过 `test_prod_task_3` 测试")
    def test_prod_task_3(self):
        ''' 测试线上失败任务3
        @报错原因：apple_podcast_plugin_handler error, apple_podcast_plugin_handler_web匹配失败, 未能正确解析MP3信息
        @报错日期：2025年4月3日 15:21
        '''
        task_data = {'type': '', 'owner': '', 'publisher': 'thebookvoice.com', 'p_id': '1805998074', 'source': 'apple_podcast', 'label': [''], 'source_url': 'https://podcasts.apple.com/ma/podcast/arabic-%D8%A7%D9%84%D8%AC%D8%B2%D8%A7%D8%B1-by-%D8%AD%D8%B3%D9%86-%D8%A7%D9%84%D8%AC%D9%86%D8%AF%D9%8A/id1805998074?i=1000701831646', 'encoding': '', 'storage_location': 'obs://obs-prod-hw-bj-bdt-multimodel/multimodel.db/apple_podcast_multilingual_video', 'metadata_location': 'cosn://cos-prod-tc-bj-bdt-delta-1302248489/multimodel.db/youtube_multilingual_video', 'security': '', 'resolution': 0}
        result = apple_podcast_crawler_plugin(url=task_data["source_url"], other_data=task_data, worker_id=self.worker_id, server_name=self.server_name)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()

