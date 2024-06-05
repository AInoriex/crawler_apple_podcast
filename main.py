from handler.google_api import Gsearch, ParseApplePodcastUserId, SaveUrlToDb, SaveUrlsToDb
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
	SaveUrlsToDb(batch_id=batch_id, keyword=search_word, url_list=search_url_list)

	logger.info("[MAIN Google END]")
	return


def main_apple_podcast():
	logger.info("[MAIN Podcast START]")
	# google_search_list = [] #Google搜索链接数
	# Gsearch(search_word="site:https://podcasts.apple.com/us/podcast/", start=0, search_total=100, pause=100)

	# get urls from database

	# parse and format google search's url into api's url
	# GetApplePodcastUserId()
	search_url_list = [
		# "https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/1261944206/episodes",
		"https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/1210902931/episodes",
		# "https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/1167164482/episodes",
		# "https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/151485663/episodes",
		# "https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/1195206601/episodes",
		# "https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/1608043151/episodes",
		# "https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/1168154281/episodes",
		# "https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/1205352558/episodes",
		# "https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/1220985045/episodes",
		# "https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/918896288/episodes",
	]
	# search_url = "https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/1261944206/episodes"

	for url in search_url_list:
		try:
			single_apple_podcast(url)
		except Exception as e:
			logger.error(f"[MAIN Podcast ERROR] {e}")
			continue
		else:
			logger.info(f"[MAIN Podcast SUCC] {url}")

	logger.info("[MAIN Podcast END]")
	

def single_apple_podcast(search_url:str):
	logger.info("[Single Podcast START]")
	cfg = load_cfg("config.json")
	OUTPUT_COUNT = cfg["common"]["output_count"] 
	count = 0 #已爬取数量
	output_result_list = [] #JSON结果汇总

	while 1:
		# 爬取前变量初始化
		count += 1
		res_list = []
		# # 解析url.params
		parsed_url = urlparse(search_url)
		search_url = search_url.split("?")[0]

		# 数据抓取
		next_url, res_list = apple_podcast_api.ApplePodcastsHandler(url=search_url, params=parse_qs(parsed_url.query))
		logger.info(f"[Single Podcast] ApplePodcastsHandler, next_url:{next_url}, res_list:{res_list}")
		search_url = next_url
		if len(res_list) <= 0:
			logger.warn(f"[Single Podcast] get empty result list, please check the ApplePodcastsHandler")
		else:
			# 爬取结果存储
			if len(output_result_list) <= 0:
				output_result_list = res_list
			else:
				output_result_list += res_list
			if len(output_result_list) >= OUTPUT_COUNT:
				logger.info(f"[Single Podcast] save json cache to local file, now_count:{len(output_result_list)}, output_count:{OUTPUT_COUNT}")
				save_succ = save_json_to_file(output_result_list)
				if not save_succ:
					logger.error("[Single Podcast] save json cache file FAILED")
					pprint(output_result_list)
					return
				output_result_list = []
		
		# BREAK
		if next_url == "":
			logger.warn("[Single Podcast] EMPTY next_url, break the apple_podcast handler")
			break
		# if count > 3:
		# 	logger.debug("[Single Podcast] debug break")
		# 	break

		# SLEEP
		random_sleep(rand_st=10, rand_range=5)

	# save result before exit
	logger.info(f"[Single Podcast] json cache save to local file, now_count:{len(output_result_list)}, output_count:{OUTPUT_COUNT}")
	save_succ = save_json_to_file(output_result_list)
	if not save_succ:
		logger.error("[Single Podcast] save final json file FAILED")
		pprint(output_result_list)

	logger.info("[Single Podcast END]")
	return


def main():
	print("Only the option `google` or `podcast` can launch program.")
	return


if __name__ == "__main__":
	import sys
	if sys.argv[1] == "google":
		main_google_search()
	elif sys.argv[1] == "podcast":
		main_apple_podcast()
	else:
		main()
	print("== Program Exit ==")
	input()