__author__ = 'Almenon'

from urllib.request import urlopen
from urllib import error
from json import loads
import logging
logging.basicConfig(level="DEBUG")  # set level to INFO to get rid of debug messages

netflix_link = "http://www.netflix.com/title/"
api_url = 'http://netflixroulette.net/api/api.php?title='
class CustomError(Exception):
    pass


def get_netflix_id(title):
    global netflix_link
    global api_url

    post_request = title.replace(' ', '+')
    url = api_url + post_request
    logging.info(url)

    try:
        data = urlopen(url)
    except error.HTTPError as e:
        if e.code == 404:
            logging.info(title + " is not on netflix")
            return None
        else: # yay for syntactic sugar
            raise CustomError("HTTP error: " + str(e.code))

    json_data = data.read().decode('utf-8')
    logging.debug("json data:" + json_data)
    parsed_json = loads(json_data)
    logging.info("JSON: " + str(parsed_json))

    if 'error' not in parsed_json:
        netflix_link += str(parsed_json['show_id'])
        logging.info(netflix_link)
        return netflix_link
    else:
        raise CustomError("netflix roulette returned error in json: \n" + str(parsed_json))

# print(get_netflix_id("Attack on Titan")) # uncomment this to test
# thanks to http://netflixroulette.net/api/
# function modified from get_netflix_id in NetflixRouletteAPI wrapper
