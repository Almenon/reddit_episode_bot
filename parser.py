__author__ = 'Almenon'

from re import compile, search
import logging
from word2num import word2num
logging.basicConfig(level="DEBUG") # set level to INFO to get rid of debug messages

seNumberRegex = compile(r"\b(s|e)[a-s]*\ *?(\w+)"  # season or episode X
                r"[\: ,_\[\]\-x]*"        # followed by optional seperator
                r"(s|e)[a-s]*\ *?(\w+)")   # season/episode X
# example match:  /u/the_episode_bot pokemon S01E06

class ParseError(Exception):
    pass


def parse(request):
    logging.info("request: " + request)

    # PARSE REQUEST
    request = request.lower()
    season_episode = search(seNumberRegex, request)
    if season_episode is None:
        raise ParseError("request does not contain correct format: regex found no match")
    elif season_episode.group(1) is 'e' and season_episode.group(3) is 's':
        episode = season_episode.group(2)
        season = season_episode.group(4)
    elif season_episode.group(1) is 's' and season_episode.group(3) is 'e':
        season = season_episode.group(2)
        episode = season_episode.group(4)
    else: raise ParseError("request does not contain correct format: input is season/season or ep/ep")

    episodeNum = word2num(episode)
    seasonNum = word2num(season)
    if episodeNum is None or seasonNum is None:
        raise ParseError("request does not contain correct format: s=" + season + " e=" + episode)

    return seasonNum, episodeNum