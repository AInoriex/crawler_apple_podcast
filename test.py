from handler.apple_podcast_episode import ApplePodcastsHandler
from utils.logger import logger
from utils.tool import load_cfg

cfg = load_cfg("config.json")

# episode_id = "1261944206"
episode_id = "1564113869"
current_url = f"https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/{episode_id}/episodes?l=en-US&offset=20"
next_url = ApplePodcastsHandler(url=current_url)
logger.info(f"[ApplePodcastsHandler] get next_url:{next_url}")
