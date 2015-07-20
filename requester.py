__author__ = 'Almenon'

import time
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib import error
from json import loads
from re import compile,search
import logging
logging.basicConfig(level="DEBUG") # set level to INFO to get rid of debug messages

error_msg = "None"
base = "http://www.omdbapi.com/?"
regex = compile(r"(?:\"([^\"]+)\"[ ,]*)??"  # "show title" (optional)
                r"(s|e)[a-s]*\ *?(\d+)[ ,]*" # season X ,
                r"(?:s|e)[a-s]*\ *?(\d+)")


# many other possible string inputs i could check for:
"""
   Season X (info on entire season)
   episode X (season 1 assumed)
   episode X-X or X,X.. (info on multiple episodes)
   episode "title" (would need a database of titles)
   episode X season X (some people might write in reversed order)
   episode X [rating|actors|date|...] (request a certain piece of info)
   X best episodes (sort by review and return X episodes)
"""

def parse(request):
    logging.debug("request: " + request)
    # PARSE REQUEST
    request = request.lower()
    show_season_episode = search(regex,request)
    if show_season_episode is None:
        error_msg = "request does not contain correct format"
        logging.info(error_msg)
        return None
    #keyrequest = None # possible future feature: return only a certain key/value pair
    if show_season_episode.group(1) is not None: show = show_season_episode.group(1)
    if show_season_episode.group(2) is 'e': # format is episode season
        episode = show_season_episode.group(3)
        season = show_season_episode.group(4)
    else: # format is season episode
        season = show_season_episode.group(3)
        episode = show_season_episode.group(4)

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
            error_msg = "There was an error when getting data from omdbapi.  Possibly the site is offline: " + \
                        "400 error: invalid GET request"
            logging.warning(error_msg)
        else:
            error_msg = "There was an error when getting data from omdbapi.  Possibly the site is offline: " + e.code
            logging.warning(error_msg)
        return None


    # PARSE JSON & return requested data
    # thanks to http://stackoverflow.com/questions/6541767
    jsonData = data.read().decode('utf-8')
    logging.debug(jsonData)
    parsedJson = loads(jsonData)
    logging.info("JSON: " + str(parsedJson))
    if len(parsedJson) == 2: # checks if JSON is {'Response': 'False', 'Error': 'Series or episode not found!'}
        error_msg = post_request + " returns error.  That episode or show is not in the database"
        logging.info(error_msg)
        return None
    requestedInfo = ""
    for key in ('Title','Plot','imdbRating', "Year"):
        requestedInfo += key + ": " + parsedJson[key] + "\n\n"
    return requestedInfo
    # http://www.omdbapi.com/?t=Game of Thrones&Season=1&Episode=1

# helper function
def printall(dictionary):
    for key in dictionary:
        print(key + " : " + dictionary[key])

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