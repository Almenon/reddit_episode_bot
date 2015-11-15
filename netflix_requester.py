__author__ = 'Almenon'

from urllib.request import urlopen
from urllib import error
from json import loads
import logging
logging.basicConfig(level="DEBUG")  # set level to INFO to get rid of debug messages

netflix_links = { # hardcoded links for important subreddits in case netflix website fails
    'bojack horseman': 'http://www.netflix.com/title/80019503',
    'orange is the new black': 'http://www.netflix.com/title/70242311'
}
netflix_url = "http://www.netflix.com/title/"
api_url = 'http://netflixroulette.net/api/api.php?title='
english_letters = "aeiouun"
accent_letters = b'\xc3\xa1\xc3\xa9\xc3\xad\xc3\xb3\xc3\xba\xc3\xbc\xc3\xb1'.decode()
 # above is equivalent to "áéíóúüñ".encode().decode()
 # i should be able to just type "áéíóúüñ" and be done with it
 # probably has to do with the project encoding (file - settings - editor - file encodings in pycharm)
 # but it works so i'm not going to mess with it


class CustomError(Exception):
    pass


def get_netflix_link(title):
    """
    :param title: of a show
    :return: link to instant watch show on Netflix.  None if show is not listed in netflixroulette
    :raise:  CustomError if the website is down, JSON has the word error, or link doesn't work
    """

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
            if e.code == 522: logging.info("connection timed out")
            if title in netflix_links:
                logging.warning("HTTP error in netflix_requester:" + str(e.code) + '\n' + url)
                return netflix_links[title]
            else:
                logging.info(title + ' netflix link is not hardcoded in')
                raise CustomError("HTTP error in netflix_requester: " + str(e.code) + '\n' + url)

    json_data = data.read().decode('utf-8')
    logging.debug("json data:" + json_data)
    parsed_json = loads(json_data)
    logging.info("JSON: " + str(parsed_json))

    if 'error' not in parsed_json:
        netflix_link = netflix_url + str(parsed_json['show_id'])
        logging.info(netflix_link)
        try:
            urlopen(netflix_link) # make sure link works
        except error.URLError as e:
            raise CustomError("netflix link is incorrect: " + e.msg + ' ' + e.code)
        return netflix_link
    else:
        raise CustomError("Netflix roulette returned error in json: \n" + str(parsed_json) + '\n' + url)

print(get_netflix_link("bojack horseman")) # uncomment this to test
    # todo: figure out why this file can't be run on its own (low importance)
    # SyntaxError: Non-UTF-8 code starting with '\xe1' in file C:/dev/PycharmProjects/reddit_episode_bot/netflix_requester.py
    # on line 13, but no encoding declared; see http://python.org/dev/peps/pep-0263/ for details

# thanks to http://netflixroulette.net/api/
# function modified from get_netflix_id in NetflixRouletteAPI wrapper
