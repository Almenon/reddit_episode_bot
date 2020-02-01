__author__ = 'Almenon'

from re import compile, search
import logging
logging.basicConfig(level="DEBUG") # set level to INFO to get rid of debug messages
from word2number import w2n

complexRegex = compile(r"\b(s|e)[a-s]*\ *?(\w+)"  # season or episode X
                r"[\: ,_\[\]\-x]*"        # followed by optional seperator
                r"(s|e)[a-s]*\ *?(\w+)")   # season/episode X
# example match:  /u/the_episode_bot pokemon S01E06
# benefits of complexity is that it can handle mispellings

seasonRegex = r"seas?on"
episodeRegex = r"eps?i?s?o(?:si)?de"
# covers common mispellings:
# epiode (episode)
# eposide (episode)
# epsiode (episode)
# seaon (season)

seperator = r"[\: ,_\[\]\-x]*"

simpleRegexSE = compile(r"s +(\w+)" + seperator + "ep? +(\w+)")
simpleRegexES = compile(r"ep? +(\w+)" + seperator + "s +(\w+)")
simpleRegexSEFull = compile(seasonRegex + r" +(\w+)" + seperator + episodeRegex + r" +(\w+)")
simpleRegexESFull = compile(episodeRegex + r" +(\w+)" + seperator + r"seas?on +(\w+)")


class ParseError(Exception):
    pass


def parse_simple(request):
    """
    :return: show, season number, episode number
    """
    SE = search(simpleRegexSE, request)
    ES = search(simpleRegexES, request)
    if SE is not None:
        season = SE.group(1)
        episode = SE.group(2)
    elif ES is not None:
        season = ES.group(2)
        episode = ES.group(1)
    else: return None, None

    episodeNum = w2n.word_to_num(episode)
    seasonNum = w2n.word_to_num(season)

    return seasonNum, episodeNum


def parse_complex(request):
    season_episode = search(complexRegex, request)
    if season_episode is None:
        raise ParseError("request does not contain correct format: regex found no match")
    elif season_episode.group(1) is 'e' and season_episode.group(3) is 's':
        episode = season_episode.group(2)
        season = season_episode.group(4)
    elif season_episode.group(1) is 's' and season_episode.group(3) is 'e':
        season = season_episode.group(2)
        episode = season_episode.group(4)
    else: raise ParseError("request does not contain correct format: "
                           "input is season/season or ep/ep. " + str(season_episode.groups()))

    episodeNum = w2n.word_to_num(episode)
    seasonNum = w2n.word_to_num(season)
    if episodeNum is None or seasonNum is None:
        raise ParseError("could not convert to number: s=" + season + " e=" + episode)

    return seasonNum, episodeNum


def parse(request):
    """
    :return: season number, episode number
    """
    logging.info("request: " + request)

    request = request.lower()
    season, episode = parse_simple(request)

    if season is None or episode is None:
        season, episode = parse_complex(request)


    return season, episode