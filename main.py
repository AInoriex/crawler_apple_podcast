from handler.google_api import Gsearch, SaveUrlsToDb, ParseApplePodcastUserId
from handler.apple_podcast_api import ApplePodcastsHandler
from handler.magic_api import CrawlerSearchInfo
from utils.utime import random_sleep
from utils.logger import init_logger
from utils.file import save_json_to_file
from utils.tool import load_cfg
from utils.lark import alarm_lark_text
from pprint import pprint

logger = init_logger("main")
cfg = load_cfg("config.json")

def main_google_search():
	logger.info("[MAIN Google START]")

	batch_id = "TEST_BATCH_240524_04"
	search_word = "site:https://podcasts.apple.com/us/podcast/"
	search_total = 5000
	logger.info(f"[MAIN Google PARAMS] batch_id:{batch_id} | search_word:{search_word} | search_total:{search_total}")

	search_url_list = Gsearch(search_word=search_word, start=200, search_total=search_total, pause=60)
	# print(search_url_list)

	# user_id_list = [ParseApplePodcastUserId(url) for url in search_url_list]
	# print(user_id_list)

	# for url in search_url_list:
	# 	SaveUrl(batch_id=batch_id, keyword=search_word, url=url)
	SaveUrlsToDb(batch_id=batch_id, keyword=search_word, url_list=search_url_list)

	logger.info("[MAIN Google END]")
	return


def main_apple_podcast():
	logger.info("[MAIN Podcast START]")
	while 1:
		# get urls from database
		pod = CrawlerSearchInfo()
		pod.GetRandomPodcast()
		if pod.id <= 0:
			logger.warn(f"GetRandomPodcast None todo url to crawl, retry after 5mins. POD.id:{pod.id}")
			random_sleep(rand_st=60*5, rand_range=5)
			continue

		# parse apple podcast user id
		query_user_id = pod.crawler_id
		if pod.crawler_id == "":
			query_user_id = ParseApplePodcastUserId()
		if query_user_id == "":
			logger.warn(f"GetRandomPodcast parse podcast user_id failed, please check the db record. POD.id:{pod.id}")
			random_sleep(rand_st=5, rand_range=5)
			continue

		try:
		# start crawler
			target_url = f"https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/{query_user_id}/episodes"
			logger.info(f"Ready to crawl the url {target_url}. Get From Id.{pod.id}")
			single_apple_podcast(target_url)

		except KeyboardInterrupt:
			logger.error(f"[MAIN Podcast KeyboardInterrupt] Block the crawler.")
			pod.status = pod.CRAWLSTATUSFAIL
			pod.UpdatePodcastStatus()
			break

		except Exception as e:
			logger.error(f"[MAIN Podcast ERROR] {e.args}")
			# pod.status = pod.CRAWLSTATUSFAIL
			# pod.UpdatePodcastStatus()
			
		else:
			logger.info(f"[MAIN Podcast SUCC] crawl {target_url} done.")

		finally:
			pod.status = pod.CRAWLSTATUSOK
			pod.UpdatePodcastStatus()
			alarm_lark_text(cfg["lark_conf"]["webhook"], f"crawl user_id:{pod.crawler_id}s' podcasts done. \
				\n\ttarget_url: {target_url} \
				\n\trecord_id: {pod.id} \
				\n\trecord_status: {pod.status}")
			random_sleep(rand_st=5, rand_range=5)
			continue
	logger.info("[MAIN Podcast END]")
	

def single_apple_podcast(search_url:str):
	logger.info("[Single Podcast START]")
	OUTPUT_COUNT = cfg["common"]["output_count"] 
	count = 0 #已爬取数量
	output_result_list = [] #JSON结果汇总

	while 1:
		# 爬取前变量初始化
		count += 1
		res_list = []

		# 数据抓取
		next_url, res_list = ApplePodcastsHandler(url=search_url)
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
			logger.warn(f"[Single Podcast] EMPTY next_url, break the apple_podcast handler. count:{count}")
			break

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