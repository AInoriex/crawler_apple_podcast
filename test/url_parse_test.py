from urllib.parse import urlparse, parse_qs

if __name__ == "__main__":
    url = 'https://someurl.com/with/query_string?i=main&mode=front&sid=12ab&enc=+Hello'
    url = '/v1/catalog/us/podcasts/1261944206/episodes?l=en-US&offset=30'
    parsed_url = urlparse(url)
    # print("parsed_url.geturl", parsed_url.geturl())
    # print("parsed_url.scheme", parsed_url.scheme)
    # print("parsed_url.hostname", parsed_url.hostname)
    # print("parsed_url.path", parsed_url.path)
    print(url.split("?")[0])
    print("parse_qs(parsed_url.query)", parse_qs(parsed_url.query), len(parse_qs(parsed_url.query)))