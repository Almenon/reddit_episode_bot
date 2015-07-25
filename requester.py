__author__ = 'Almenon'

from urllib.request import urlopen
from urllib.parse import urlencode
from urllib import error
from json import loads
import logging
logging.basicConfig(level="DEBUG") # set level to INFO to get rid of debug messages

error_msg = "None"
base = "http://www.omdbapi.com/?"


class CustomError(Exception):
    pass

def get_info(show='Game of thrones', season=1, episode=1):
    """
    returns title, plot, rating, and year
    """
    global error_msg

    post_request = urlencode([('t',show), ('Season',season), ('Episode',episode)])
    logging.info("Parsed request is " + base + post_request)

    # get data from omdbapi.com
    try:
        data = urlopen(base + post_request)
    except error.HTTPError as e:
        if e.code == 400:
            logging.warning(error_msg)
            raise CustomError("There was an error when getting data from omdbapi.  Possibly the site is offline: " + \
                        "400 error: invalid GET request")
        else:
            logging.warning(error_msg)
            raise CustomError("There was an error when getting data from omdbapi.  "
                              "Possibly the site is offline: " + e.code)


    # PARSE JSON & return requested data
    # thanks to http://stackoverflow.com/questions/6541767
    jsonData = data.read().decode('utf-8')
    logging.debug(jsonData)
    parsedJson = loads(jsonData)
    logging.info("JSON: " + str(parsedJson))
    if len(parsedJson) == 2: # checks if JSON is {'Response': 'False', 'Error': 'Series or episode not found!'}
        logging.info(error_msg)
        raise CustomError(post_request + " returns error.  That episode or show is not in the database")
    requestedInfo = ""
    for key in ('Title','Plot','imdbRating', "Year"):
        requestedInfo += key + ": " + parsedJson[key] + "\n\n"
    return requestedInfo
    # todo: return IMDB link
    # http://www.omdbapi.com/?t=Game of Thrones&Season=1&Episode=1

# output = get_info(" test string ")
# print(output)

""""
 LINKS:
 http://www.omdbapi.com/
 check results against http://www.imdb.com/list/ls053752699/
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