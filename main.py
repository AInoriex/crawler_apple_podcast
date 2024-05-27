from handler.google_api import Gsearch, GetApplePodcastUserId, SaveUrl, SaveUrls
from handler import apple_podcast_api
from utils.utime import random_sleep
from utils.logger import init_logger
from utils.file import save_json_to_file
from utils.tool import load_cfg
from urllib.parse import urlparse, parse_qs
from pprint import pprint

logger = init_logger("main")

def main_google_search():
	logger.info("[MAIN Google START]")

	batch_id = "TEST_BATCH_240524_04"
	search_word = "site:https://podcasts.apple.com/us/podcast/"
	search_total = 5000
	logger.info(f"[MAIN Google PARAMS] batch_id:{batch_id} | search_word:{search_word} | search_total:{search_total}")

	search_url_list = Gsearch(search_word=search_word, start=200, search_total=search_total, pause=60)
	# print(search_url_list)

	# user_id_list = [GetApplePodcastUserId(url) for url in search_url_list]
	# print(user_id_list)

	# for url in search_url_list:
	# 	SaveUrl(batch_id=batch_id, keyword=search_word, url=url)
	SaveUrls(batch_id=batch_id, keyword=search_word, url_list=search_url_list)

	logger.info("[MAIN Google END]")
	return


def main_apple_podcast():
	logger.info("[MAIN Podcast START]")
	cfg = load_cfg("config.json")
	OUTPUT_COUNT = cfg["common"]["output_count"] 

	google_search_list = [] #Google搜索链接数
	Gsearch(search_word="site:https://podcasts.apple.com/us/podcast/", start=0, search_total=100, pause=100)

	count = 0 #已爬取数量
	output_result_list = [] #JSON结果汇总
	GetApplePodcastUserId()

	search_url = "https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/1261944206/episodes"

	while 1:
		# 爬取前变量初始化
		count += 1
		res_list = []
		# # 解析url.params
		parsed_url = urlparse(search_url)
		search_url = search_url.split("?")[0]

		# 数据抓取
		next_url, res_list = apple_podcast_api.ApplePodcastsHandler(url=search_url, params=parse_qs(parsed_url.query))
		logger.info(f"[MAIN Podcast] ApplePodcastsHandler, next_url:{next_url}, res_list:{res_list}")
		
		# 爬取结果后处理
		search_url = next_url
		if len(output_result_list) <= 0:
			output_result_list = res_list
		else:
			output_result_list += res_list
		if len(output_result_list) >= OUTPUT_COUNT:
			logger.info(f"[MAIN Podcast] save json cache to local file, now_count:{len(output_result_list)}, output_count:{OUTPUT_COUNT}")
			save_succ = save_json_to_file(output_result_list)
			if not save_succ:
				logger.error("[MAIN Podcast] save json cache file FAILED")
				pprint(output_result_list)
				return
			output_result_list = []
		
		# BREAK
		if next_url == "":
			logger.warn("[MAIN Podcast] EMPTY next_url, break the apple_podcast handler")
			break
		if count > 3:
			logger.debug("[MAIN Podcast] debug break")
			break

		# SLEEP
		random_sleep(rand_st=10, rand_range=5)

	# save result before exit
	logger.info(f"[MAIN Podcast] json cache save to local file, now_count:{len(output_result_list)}, output_count:{OUTPUT_COUNT}")
	save_succ = save_json_to_file(output_result_list)
	if not save_succ:
		logger.error("[MAIN Podcast] save final json file FAILED")
		pprint(output_result_list)

	logger.info("[MAIN Podcast END]")
	return


def main():
	print("Nothing in main")
	return


if __name__ == "__main__":
	import sys
	if sys.argv[1] == "google":
		main_google_search()
	elif sys.argv[1] == "podcast":
		main_apple_podcast()
	else:
		main()