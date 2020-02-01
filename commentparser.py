__author__ = 'Almenon'

from re import compile, search
import logging
logging.basicConfig(level="DEBUG") # set level to INFO to get rid of debug messages
from word2number import w2n

regex = compile(r"(?:\/u\/the_episode_bot[ ,:]*(\S+(?:\ \S+\b)*)[ ,]+)?"  # bot's username followed by title (optional)
                r"\b(s|e)[a-s]*\ *?(\w+)[\: ,_\[\]\-x]*"  # season or episode followed by optional seperator
                r"(s|e)[a-s]*\ *?(\w+)")   # season/episode
# example match:  /u/the_episode_bot pokemon S01E06

# simple regex needed because complex regex can fail in some cases
simpleRegexSE = compile(r"/u/the_episode_bot[: ]+(.*)season +(\w+)[\: ,_\[\]\-x]*episode +(\w+)")
simpleRegexES = compile(r"/u/the_episode_bot[: ]+(.*)episode +(\w+)[\: ,_\[\]\-x]*season +(\w+)")

class ParseError(Exception):
    pass


def parse_simple(request):
    """
    :return: show, season number, episode number
    """
    SE = search(simpleRegexSE, request)
    ES = search(simpleRegexES, request)
    if SE is not None:
        season = SE.group(2)
        episode = SE.group(3)
    elif ES is not None:
        season = ES.group(3)
        episode = ES.group(2)
    else: return None, None, None

    show = SE.group(1)
    episodeNum = w2n.word_to_num(episode)
    seasonNum = w2n.word_to_num(season)

    return show, seasonNum, episodeNum


def parse_complex(request):
    """
    :return: show, season number, episode number
    """
    show_season_episode = search(regex,request)
    if show_season_episode is None:
        raise ParseError("request does not contain correct format: regex found no match")
    elif show_season_episode.group(2) is 'e' and show_season_episode.group(4) is 's':
        episode = show_season_episode.group(3)
        season = show_season_episode.group(5)
    elif show_season_episode.group(2) is 's' and show_season_episode.group(4) is 'e':
        season = show_season_episode.group(3)
        episode = show_season_episode.group(5)
    else: raise ParseError("request does not contain correct format: input is season/season or ep/ep")

    show = show_season_episode.group(1)

    episodeNum = w2n.word_to_num(episode)
    seasonNum = w2n.word_to_num(season)
    if episodeNum is None or seasonNum is None:
        raise ParseError("could not convert to number: s=" + season + " e=" + episode)

    return show, seasonNum, episodeNum

def parse(request):
    """
    :return: show, season number, episode number
    """
    logging.info("request: " + request)

    request = request.lower()
    show, season, episode = parse_simple(request)

    if season is None or episode is None:
        show, season, episode = parse_complex(request)

    return show, season, episode