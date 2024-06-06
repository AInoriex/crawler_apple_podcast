from handler.google_api import Gsearch, SaveUrlsToDb, ParseApplePodcastUserId
from handler.apple_podcast_api import ApplePodcastsHandler
from handler.magic_api import CrawlerSearchInfo
from utils.utime import random_sleep, get_now_time_string
from utils.logger import init_logger
from utils.tool import load_cfg
from utils.lark import alarm_lark_text
from utils.ip import get_local_ip, get_public_ip
from traceback import format_exception # Python 3.10+

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
	#采集失败计数, 连续三次退出处理
	crawl_fail_count = 0 
	crawl_fail_limit = 3
	while 1:
		# 从数据库获取待采集用户id
		pod = CrawlerSearchInfo()
		pod.GetRandomPodcast()
		if pod.id <= 0:
			logger.warn(f"GetRandomPodcast None todo url to crawl, retry after 5mins. POD.id:{pod.id}")
			random_sleep(rand_st=60*5, rand_range=5)
			continue

		# 解析链接的用户id生成请求数据抓取API
		query_user_id = pod.crawler_id
		if pod.crawler_id == "":
			query_user_id = ParseApplePodcastUserId()
		if query_user_id == "":
			logger.warn(f"GetRandomPodcast parse podcast user_id failed, please check the db record. POD.id:{pod.id}")
			random_sleep(rand_st=5, rand_range=5)
			continue

		start_url = f"https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/{query_user_id}/episodes"
		logger.info(f"Ready to crawl the url {start_url}. Get From Id.{pod.id}")
		count = 0
		current_url = start_url
		# 单个用户数据采集
		try:
			while 1:
				next_url = ApplePodcastsHandler(url=current_url)
				logger.info(f"[ApplePodcastsHandler] get next_url:{next_url}")
				current_url = next_url
				if current_url == "":
					logger.warning(f"[ApplePodcastsHandler] get EMPTY next_url, break the apple_podcast handler. count:{count}".format(count=count+1))
					break	

		except KeyboardInterrupt:
			crawl_fail_count += 1
			logger.error(f"[MAIN Podcast Keyboard Interrupt] Block the crawler.")
			pod.status = pod.CRAWLSTATUSFAIL
			pod.UpdatePodcastStatus()
			report_to_lark(pod, start_url, exception_string=err)
			break

		except Exception as e:
			crawl_fail_count += 1
			err = "".join(format_exception(e)).strip()
			logger.error(f"[MAIN Podcast ERROR] {err}")
			pod.status = pod.CRAWLSTATUSFAIL
			pod.UpdatePodcastStatus()
			report_to_lark(pod, start_url, exception_string=err)
			if crawl_fail_count >= crawl_fail_limit:
				logger.error(f"[MAIN Podcast FailToMuch Interrupt] Break the crawler.")
				alarm_lark_text(webhook=cfg["lark_conf"]["webhook"],
					text="[ATTENTIONS] 播客采集进程中止！失败次数过多，中断采集. 机器IP:"+get_local_ip())
				break
		else:
			crawl_fail_count = 0
			logger.info(f"[MAIN Podcast SUCC] crawl {start_url} done.")
			pod.status = pod.CRAWLSTATUSOK
			pod.UpdatePodcastStatus()
			report_to_lark(pod, start_url)

		finally:
			random_sleep(rand_st=5, rand_range=5)		
	logger.info("[MAIN Podcast END]")


def main():
	print("Only the option `google` or `podcast` can launch program.")
	return


def report_to_lark(pod:CrawlerSearchInfo, start_url:str, exception_string=""):
	''' 飞书机器人通知 '''
	local_ip = get_local_ip()
	public_ip = get_public_ip()
	now_time_str = get_now_time_string()
	title = ""
	if pod.status == CrawlerSearchInfo.CRAWLSTATUSFAIL:
		title = f"[ERROR] Apple播客 user_id:{pod.crawler_id} 采集失败. \n\t错误信息: {exception_string}"
	elif pod.status == CrawlerSearchInfo.CRAWLSTATUSSUCC:
		title = f"[INFO] Apple播客 user_id:{pod.crawler_id} 采集成功."
	else:
		title = f"[DEBUG] Apple播客 user_id:{pod.crawler_id} 采集未知状态：{pod.status}."
	alarm_lark_text(webhook=cfg["lark_conf"]["webhook"], 
		text=f"{title} \
		\n\t用户主页: {pod.result_url} \
		\n\t数据库记录id: {pod.id} \
		\n\t起始Url: {start_url} \
		\n\tLocal_IP:{local_ip} \
		\n\tPublic_IP:{public_ip} \
		\n\tTime:{now_time_str}")

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