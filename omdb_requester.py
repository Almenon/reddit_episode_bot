__author__ = 'Almenon'

from urllib.request import urlopen
from urllib.parse import quote
from urllib.parse import urlencode
from urllib import error
from json import loads
from os import environ
import logging
logger = logging.getLogger(__name__)

base = "http://www.omdbapi.com/?"
apiKey = environ['omdbApiKey']

class OmdbError(Exception):
    """
    raised for any error in omdb_requester
    """
    pass


def get_info(show='Game of thrones', season=1, episode=1):
    """
    :param show: string
    :param season: whole number
    :param episode: whole number
    :return: formatted String with information about the show.
    :raises: CustomError if show is not in omdb or omdb is down
    """

    post_request = urlencode([('apikey', apiKey),('t', show), ('Season', season), ('Episode', episode)],quote_via=quote)
    # quote_via=quote because + doesn't work in some cases
    logging.info("Parsed request is " + base + post_request)

    # get data from omdbapi.com
    try:
        data = urlopen(base + post_request)
        # url looks like this:
        # http://www.omdbapi.com/?t=Game%20of%20Thrones&Season=1&Episode=1
    except error.URLError as e:
        raise OmdbError("There was an error when getting data from omdbapi.  "
                          "Possibly the site is offline: error code " + str(e.code))
        # 400 or 404 error indicates site is offline.
        # 403 indicates Forbidden

    # PARSE JSON & return requested data
    # thanks to http://stackoverflow.com/questions/6541767
    json_data = data.read().decode('utf-8')
    logging.debug(json_data)
    parsed_json = loads(json_data)
    logging.info("JSON: " + str(parsed_json))
    if len(parsed_json) == 2:  # checks if JSON is {'Response': 'False', 'Error': 'Series or episode not found!'}
        raise OmdbError(base + post_request + " returns error.  That episode or show is not in the database")
    try:
        urlopen("http://www.imdb.com/title/" + parsed_json['imdbID']) # verify imdb is correct
    except error.URLError as e:
        raise OmdbError("imdb link is incorrect: " + e.msg + ' ' + e.code)
    return parsed_json



# for testing:
# try:
#     output = get_info("bojack horseman", season=2,episode=7)
#     print(output)
# except CustomError as e:
#     print(e)


def verify_show(show, season, number_episodes):
    """
    helper function to check if omdb as all the episodes of a show in its database
    not complete yet
    """
    raise NotImplementedError

    for i in range(1,50):
        try:
            output = get_info(show, season, episode)
            print(output)
        except OmdbError as e:
            print(e)
            if had_error:
                episode = 0
                season += 1

            had_error = True
            continue
