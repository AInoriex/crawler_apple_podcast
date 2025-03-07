from utils.logger import logger
from utils.tool import load_cfg
from utils.request import download_resource

cfg = load_cfg("config.json")

def test_episode_handler():
    from handler.apple_podcast_episode import ApplePodcastsHandler
    # episode_id = "1261944206"
    episode_id = "1564113869"
    current_url = f"https://amp-api.podcasts.apple.com/v1/catalog/us/podcasts/{episode_id}/episodes?l=en-US&offset=20"
    next_url = ApplePodcastsHandler(url=current_url)
    logger.info(f"[ApplePodcastsHandler] get next_url:{next_url}")

def test_audio_handler():
    from handler.apple_podcast_audio import apple_podcast_plugin_handler
    from handler.apple_podcast_audio import apple_podcast_plugin_handler_web
    from handler.apple_podcast_audio import apple_podcast_plugin_handler_api
    test_url = "https://podcasts.apple.com/us/podcast/2281-elon-musk/id360084272?i=1000696846801"
    # obj, err_msg = apple_podcast_plugin_handler_web(test_url)
    obj, err_msg = apple_podcast_plugin_handler_api(test_url)
    print("返回数据:", obj)
    print("Error:", err_msg)

def test_audio_download():
    from handler.apple_podcast_audio import GetApplePodcastAudioV1
    test_url = "https://podcasts.apple.com/us/podcast/2281-elon-musk/id360084272?i=1000696846801"
    mp3_links = GetApplePodcastAudioV1(test_url)
    print("提取到的MP3链接:", mp3_links)
    if len(mp3_links) <= 0:
        return
    download_resource(url=mp3_links[0], filename="2281-elon-musk.mp3")

if __name__ == "__main__":
    # test_audio_download()
    test_audio_handler()
    pass