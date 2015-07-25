__author__ = 'Almenon'

from re import compile, search
import logging
logging.basicConfig(level="DEBUG") # set level to INFO to get rid of debug messages

regex = compile(r"(?:\"([^\"]+)\"[ ,]*)??"  # "show title" (optional)
                r"(s|e)[a-s]*\ *?(\d+)[ ,]*" # season or episode followed by optional spacing/comma
                r"(?:s|e)[a-s]*\ *?(\d+)")   # season/episode
error_msg = ''


class ParseError(Exception):
   pass

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
    global error_msg
    logging.debug("request: " + request)

    # PARSE REQUEST
    request = request.lower()
    show_season_episode = search(regex,request)
    if show_season_episode is None:
        error_msg = "request does not contain correct format"
        raise ParseError(error_msg)
        return None
    #keyrequest = None # possible future feature: return only a certain key/value pair
    if show_season_episode.group(1) is not None: show = show_season_episode.group(1)
    if show_season_episode.group(2) is 'e': # format is episode season
        episode = show_season_episode.group(3)
        season = show_season_episode.group(4)
    else: # format is season episode
        season = show_season_episode.group(3)
        episode = show_season_episode.group(4)

    return show, season, episode