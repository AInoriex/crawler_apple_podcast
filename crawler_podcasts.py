import os
from pprint import pprint
from handler.apple_podcast_episode  import ApplePodcastsHandler
from utils.utime import random_sleep, get_now_time_string_short
from utils.logger import logger
from utils.file import save_json_to_file, write_json_to_file
from utils.tool import load_cfg
from urllib.parse import urlparse, parse_qs

def main_apple_podcast():
	logger.info("[MAIN Podcast START]")
	search_url_list = [
		# "https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/1261944206/episodes",
		# "https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/1210902931/episodes",
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
		next_url, res_list = ApplePodcastsHandler(url=search_url, params=parse_qs(parsed_url.query))
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
				write_json_to_file(output_result_list, filename=os.path.join(cfg["common"]["output_path"], "meta", f"{get_now_time_string_short()}.json"))
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
	write_json_to_file(output_result_list, filename=os.path.join(cfg["common"]["output_path"], "meta", f"{get_now_time_string_short()}.json"))

	logger.info("[Single Podcast END]")
	return

if __name__ == "__main__":
    main_apple_podcast()