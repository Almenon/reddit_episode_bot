__author__ = 'Almenon'

from urllib.request import urlopen
from urllib import error
from json import loads
import logging
logger = logging.getLogger(__name__)
netflix_link = "http://www.netflix.com/title/"
api_url = 'http://netflixroulette.net/api/api.php?title='
english_letters = "aeiouun"
accent_letters = b'\xc3\xa1\xc3\xa9\xc3\xad\xc3\xb3\xc3\xba\xc3\xbc\xc3\xb1'.decode()
# above is equivalent to "αινσϊόρ".encode().decode()
# i should be able to just type "αινσϊόρ" and be done with it
# probably has to do with the project encoding (file - settings - editor - file encodings in pycharm)
# but it works so i'm not going to mess with it
class CustomError(Exception):
    pass


def get_netflix_link(title):
    """
    :param title: of a show
    :return: link to instant watch show on netflix.  None if show is not listed in netflixroulette
    :raise:  CustomError if the website is down or JSON has the word error.
    """
    global netflix_link
    global api_url
    global accent_letters
    global english_letters

    for accent, no_accent in zip(accent_letters, english_letters):
        title = title.replace(accent, no_accent)
    post_request = title.replace(' ', '+')
    url = api_url + post_request
    logging.info(url)

    try:
        data = urlopen(url)
    except error.HTTPError as e:
        if e.code == 404:
            logging.info(title + " is not on netflix")
            return None
        else:  # yay for syntactic sugar
            raise CustomError("HTTP error in netflix_requester: " + str(e.code) + '\n' + url)

    json_data = data.read().decode('utf-8')
    logging.debug("json data:" + json_data)
    parsed_json = loads(json_data)
    logging.info("JSON: " + str(parsed_json))

    if 'error' not in parsed_json:
        netflix_link += str(parsed_json['show_id'])
        logging.info(netflix_link)
        return netflix_link
    else:
        raise CustomError("Netflix roulette returned error in json: \n" + str(parsed_json) + '\n' + url)

# print(get_netflix_link("Attack on Titan")) # uncomment this to test
    # todo: figure out why this file can't be run on its own (low importance)
    # SyntaxError: Non-UTF-8 code starting with '\xe1' in file C:/dev/PycharmProjects/reddit_episode_bot/netflix_requester.py on line 13, but no encoding declared; see http://python.org/dev/peps/pep-0263/ for details

# thanks to http://netflixroulette.net/api/
# function modified from get_netflix_link in NetflixRouletteAPI wrapper
