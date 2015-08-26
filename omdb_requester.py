__author__ = 'Almenon'

from urllib.request import urlopen
from urllib.parse import urlencode
from urllib import error
from json import loads
import logging
logger = logging.getLogger(__name__)

base = "http://www.omdbapi.com/?"


class CustomError(Exception):
    pass


def get_info(show='Game of thrones', season=1, episode=1):
    """
    :param show: string
    :param season: number
    :param episode: number
    :return: formatted String with information about the show.
    :raises: CustomError if show is not in omdb or omdb is down
    """

    post_request = urlencode([('t', show), ('Season', season), ('Episode', episode)])
    logging.info("Parsed request is " + base + post_request)

    # get data from omdbapi.com
    try:
        data = urlopen(base + post_request)
        # url looks like this:
        # http://www.omdbapi.com/?t=Game of Thrones&Season=1&Episode=1
    except error.HTTPError as e:
        raise CustomError("There was an error when getting data from omdbapi.  "
                          "Possibly the site is offline: error code " + str(e.code))
        # 400 or 404 error indicates site is offline.

    # PARSE JSON & return requested data
    # thanks to http://stackoverflow.com/questions/6541767
    json_data = data.read().decode('utf-8')
    logging.debug(json_data)
    parsed_json = loads(json_data)
    logging.info("JSON: " + str(parsed_json))
    if len(parsed_json) == 2:  # checks if JSON is {'Response': 'False', 'Error': 'Series or episode not found!'}
        raise CustomError(base+post_request + " returns error.  That episode or show is not in the database")
    requested_info = "###[" + parsed_json['Title'] + ']' + \
                     '(' + "http://www.imdb.com/title/" + parsed_json['imdbID'] + ") \n\n"
    if parsed_json["Plot"] != "N/A":
        requested_info += '[Mouseover for a brief summary](#mouseover "' + parsed_json["Plot"] + '")\n\n'
    else:
        requested_info += "No summary available.  Click on title to go to imdb page.\n\n"
    for key in ('imdbRating', 'Released'):
        if parsed_json[key] != 'N/A':
            requested_info += key + ": " + parsed_json[key] + "\n\n"
        else: continue
    return requested_info

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
    for i in range(1,50):
        try:
            output = get_info(show, season, episode)
            print(output)
        except CustomError as e:
            print(e)
            if had_error:
                episode = 0
                season += 1

            had_error = True
            continue
