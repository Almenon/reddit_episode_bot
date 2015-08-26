__author__ = 'Almenon'

from re import compile, search
import logging


regex = compile(r"(?:\/u\/the_episode_bot[ ,:]*(\S+(?:\ \S+\b)*)[ ,]+)?"  # bot's username followed by title (optional)
                r"(s|e)[a-s]*\ *?(\d+)[ ,\[\]-]*"  # season or episode followed by optional seperator
                r"(?:s|e)[a-s]*\ *?(\d+)")   # season/episode
# example match:  /u/the_episode_bot pokemon S01E06

class ParseError(Exception):
    pass


def parse(request):
    """
    :param request: string with season/episode format like SXEX.  see above regex for all accepted possibilities
    :return: 3 vars.  If string doesn't have right format CustomError is raised.
        show - None if no show, else a String
        season - a number
        episode - a number
    """
    logging.info("request: " + request)

    # PARSE REQUEST
    request = request.lower()
    show_season_episode = search(regex, request)
    if show_season_episode is None:
        raise ParseError("request does not contain correct format")
    if show_season_episode.group(1) is not None: show = show_season_episode.group(1)
    else: show = None
    if show_season_episode.group(2) is 'e': # format is episode season
        episode = show_season_episode.group(3)
        season = show_season_episode.group(4)
    else:  # format is season episode
        season = show_season_episode.group(3)
        episode = show_season_episode.group(4)

    return show, season, episode

# testing

# try:
#     answer = parse("1 :: Beers in S01E05")
#     print(answer)
# except ParseError as e:
#     print(e)
