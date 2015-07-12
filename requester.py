__author__ = 'Almenon'

import time
from urllib.request import urlopen
from urllib import error
from json import loads
from re import compile,search
import logging
logging.basicConfig(level="DEBUG") # set level to INFO to get rid of debug messages

base = "http://www.omdbapi.com/?"
series = "Game of Thrones"
lastwordfinder = "\w$" # find last word on specified line
regex = compile(r"season +(\d)" # season X
        r"(?: +episode +(\d))?") # episode X (optional)
# in future find season or episode (if show is only 1 season people might forgo the season)

# rename function
def input(request):
    """
    returns title, plot, rating, and year
    request should be a string in the form of the_episode_bot season X episode X
        or the_episode_bot "title"
    """

    # PARSE REQUEST
    request = request.lower()
    show = "t=" + series
    show = show.replace(" ","%20")
    season_episode = search(regex,request)
    if season_episode is None:
        logging.info("no season found in request")
        return None
    season = "&Season=" +season_episode.group(0)
    if len(season_episode.groups()) > 1:
        episode = "&Episode=" + season_episode.group(1)
    else:
        episode = None
        return "episode_bot currently only supports info on specific episodes, not entire seasons"

    # index = request.find("season")+7
    # while index < request.length:
    #     if index == " ": pass
    #     else: season = "&Season=" + request[index]
    # index = request.find("episode")+7
    # while index < request.length:
    #     if index == " ": pass
    #     else: season = "&Season=" + request[index]


    # old code:
    # request = request.lower()
    # show = "t=" + series
    # show = show.replace(" ","%20")
    # index = request.find("season") + 7
    # season = "&Season=" + request[index]
    # index = request.find("episode") + 8
    # episode = "&Episode=" + request[index]
    logging.info("Parsed request is " + base + show + season + episode)
    keyrequest = None # use regex to select last word

    # get data from omdbapi.com
    try:
        data = urlopen(base + show + episode + season)
    except error.HTTPError as e:
        if e.code == 404: return "404 error: site not found"
        if e.code == 400: return "invalid request"
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
        print(keyrequest + parsedJson[keyrequest])
    # thanks to http://stackoverflow.com/questions/5352546
    requestedInfo = dict((key,parsedJson[key]) for key in ('Title','Plot','imdbRating', "Year"))
    return requestedInfo
    # http://www.omdbapi.com/?t=Game of Thrones&Season=1&Episode=1

# helper function
def printall(dictionary):
    for key in dictionary:
        print(key + " : " + dictionary[key])

# output = input("Episode 1 Season 1 Year")
# if type(output) == "String":
#     print(output) # function returns string if error
# else: printall(output)

""""

 FEATURES:
 top 10 episodes (optionally: by season)
 episode info & wiki link

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