from handler.google_api import Gsearch, SaveUrlsToDb
from utils.logger import logger

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

if __name__ == "__main__":
	main_google_search()