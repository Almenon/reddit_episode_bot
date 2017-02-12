__author__ = 'Almenon'

import logging
from re import compile, search

logging.basicConfig(level="DEBUG")  # set level to INFO to get rid of debug messages

regex = compile(r"(s|e)[a-s]* *?(\d+)"  # season or episode
                r"[: ,_\[\]\-x]*"  # followed by optional seperator
                r"(s|e)[a-s]* *?(\d+)")  # season/episode


class ParseError(Exception):
    pass


def parse(request):
    logging.info("request: " + request)

    # PARSE REQUEST
    request = request.lower()
    season_episode = search(regex, request)
    if season_episode is None:
        raise ParseError("request does not contain correct format")
    elif season_episode.group(1) is 'e' and season_episode.group(3) is 's':
        episode = season_episode.group(2)
        season = season_episode.group(4)
    elif season_episode.group(1) is 's' and season_episode.group(3) is 'e':
        season = season_episode.group(2)
        episode = season_episode.group(4)
    else:  # s s or e e
        raise ParseError("request does not contain correct format")

    return season, episode

    # testing

    # try:
    #     answer = parse("yo man e3s2")
    #     print(answer)
    # except ParseError as e:
    #     print(e)
