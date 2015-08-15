__author__ = 'Almenon'

from urllib.request import urlopen
from urllib.parse import urlencode
from urllib import error
from json import loads
import logging
logging.basicConfig(level="DEBUG")  # set level to INFO to get rid of debug messages

base = "http://www.omdbapi.com/?"


class CustomError(Exception):
    pass


def get_info(show='Game of thrones', season=1, episode=1):
    """
    returns title, plot, rating, and year
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
        raise CustomError(post_request + " returns error.  That episode or show is not in the database")
    requested_info = "###[" + parsed_json['Title'] + ']' + \
                    '(' + "http://www.imdb.com/title/" + parsed_json['imdbID'] + ')' + "\n\n"
    for key in ('Plot', 'imdbRating', 'Released'):
        requested_info += key + ": " + parsed_json[key] + "\n\n"
    return requested_info

# for testing:
# output = get_info(" test string ")
# print(output)

""""
 LINKS:
https://www.reddit.com/r/raerth/comments/cw70q/reddit_comment_formatting/
 possibly use http://imdbpy.sourceforge.net/index.html
    (i think it has support for episodes as well)
    (complex to use however - might require sql)
 test on https://www.reddit.com/r/botwatch/
 I can use https://www.heroku.com/pricing for free hosting
    options - hereku (free)
    azure - (use student discount -1 yr)
    https://www.dreamspark.com/Product/Product.aspx?productid=99
    amazon (use student discount - 1 yr)
    http://aws.amazon.com/education/awseducate/
 follow guide on https://www.reddit.com/r/botwatch/comments/2261dv

"""