__author__ = 'Almenon'

from re import compile, search
import logging
logging.basicConfig(level="DEBUG") # set level to INFO to get rid of debug messages

regex = compile(r"\b(s|e)[a-s]*\ *?(\d+)"  # season or episode
                r"[\: ,_\[\]\-x]*"        # followed by optional seperator
                r"(?:s|e)[a-s]*\ *?(\d+)")   # season/episode


class ParseError(Exception):
    pass


def parse(request):
    logging.info("request: " + request)

    # PARSE REQUEST
    request = request.lower()
    season_episode = search(regex,request)
    if season_episode is None:
        raise ParseError("request does not contain correct format")
    if season_episode.group(1) is 'e': # format is episode season
        episode = season_episode.group(2)
        season = season_episode.group(3)
    else:  # format is season episode
        season = season_episode.group(2)
        episode = season_episode.group(3)

    return season, episode

# testing

# try:
#     answer = parse("1 :: Beers in S01E05")
#     print(answer)
# except ParseError as e:
#     print(e)