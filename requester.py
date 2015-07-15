__author__ = 'Almenon'

import time
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib import error
from json import loads
from re import compile,search
import logging
logging.basicConfig(level="DEBUG") # set level to INFO to get rid of debug messages

base = "http://www.omdbapi.com/?"
show = "Game of Thrones"
regex = compile(r"(?:\"(.+)\")? +" # "title" (optional)
                r"season +(\d+)"    # season X
                r" *,? +"           # space with optional comma
                r"episode +(\d+)")  # episode X

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

# todo: rename function
def get_info(request):
    """
    returns title, plot, rating, and year
    request should be a string in the form of season X episode X
    """
    logging.debug(request)
    # PARSE REQUEST
    request = request.lower()
    show_season_episode = search(regex,request)
    if show_season_episode is None:
        logging.info("request does not contain correct format")
        return None
    keyrequest = None # possible future feature: return only a certain key/value pair
    if show_season_episode.group(1) is not None: show = show_season_episode.group(1)
    season = show_season_episode.group(2)
    episode = show_season_episode.group(3)
    post_request = urlencode({'t':show, 'Season':season, 'Episode':episode})
    logging.info("Parsed request is " + base + post_request)

    # get data from omdbapi.com
    try:
        data = urlopen(base + post_request)
    except error.HTTPError as e:
        if e.code == 404: return "404 error: site not found"
        if e.code == 400: return "400 error: invalid request"
        else: print("error when opening site: " + e.code)
    logging.debug(data)

    # PARSE JSON & return requested data
    # thanks to http://stackoverflow.com/questions/6541767
    jsonData = data.read().decode('utf-8')
    logging.debug(jsonData)
    parsedJson = loads(jsonData)
    logging.info(parsedJson)
    # catch index errors or verify incoming data beforehand
    # select a single attribute if specified
    if keyrequest is not None:
        print(keyrequest +": " + parsedJson[keyrequest])
    requestedInfo = ""
    for key in ('Title','Plot','imdbRating', "Year"):
        requestedInfo += key + ": " + parsedJson[key] + "\n\n"
    return requestedInfo
    # http://www.omdbapi.com/?t=Game of Thrones&Season=1&Episode=1

# helper function
def printall(dictionary):
    for key in dictionary:
        print(key + " : " + dictionary[key])

# output = get_info("alright let's try this again. calling /u/the_episode_bot\n\n\"Buffy the vampire slayer\" season 1 episode 2")
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