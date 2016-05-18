__author__ = 'Caleb'

import omdb_requester
import post_parser
import commentparser
import netflix_requester
from json import load
from datetime import datetime
import logging

with open("info/subreddits.txt") as file:
    subreddit_to_show = load(file) # dictionary [subreddit name] = tv show
bot_disclaimer = "------\n" \
                 "^^I'm ^^a ^^bot ^^that ^^gives ^^info ^^on ^^shows. " \
                 "^^| ^^[message](http://www.reddit.com/message/compose?to=the_episode_bot) ^^me " \
                 "^^if ^^there's ^^an ^^issue. ^^| ^^[about](https://github.com/Almenon/reddit_episode_bot)"
# formatting for bot_disclaimer thanks to wikipediacitationbot

lastNetflixEpisode = { # last episode availible on Netflix.  9999 for series always on Netflix
    'bojack horseman': 9999,
    'orange is the new black': 9999,
    'my little pony': 5.26,
}  # note that this system only supports series with < 100 episodes per season


def format_comment(request, subreddit, post):
    """
    :param request: comment text or post title
    :param subreddit: PRAW subreddit object or name of subreddit (without the /r/)
    :param post: True if request is a post, False otherwise
    :return: a paragraph of info and links about the episode, formatted for Reddit
    :except: if any of the sub-modules called raise an exception it passes right through this module
    """

    global subreddit_to_show
    global bot_disclaimer
    released = True

    if post:
        parsedcomment = post_parser.parse(request)
        season, episode = parsedcomment
        show = subreddit_to_show[str(subreddit).lower()]
        if int(season)+int(episode)/100 > lastNetflixEpisode[show]:
            released = False

    else:
        parsedcomment = commentparser.parse(request)
        show, season, episode = parsedcomment
        if show is None:
            show = subreddit_to_show[str(subreddit).lower()]

    episode_info = omdb_requester.get_info(show, season, episode)
    answer = "#####&#009;  \n######&#009;  \n####&#009;  \n" \
             "###[{title}](http://www.imdb.com/title/{id})\n\n".format(
                title=episode_info['Title'], id=episode_info['imdbID'])
    if episode_info["Plot"] != "N/A":
        answer += '[Mouseover for a brief summary](#mouseover "' + episode_info["Plot"] + '")\n\n'
    if episode_info['Year'].isdigit() and int(episode_info['Year']) > datetime.now().year:
        released = False

    for key in ('imdbRating', 'Released'):
        if episode_info[key] != 'N/A':
            answer += key + ": " + episode_info[key] + "\n\n"
        else: continue

    if released:
        try:
            netflix_link = netflix_requester.get_netflix_link(show)
            if netflix_link is None:
                answer += "Not available on Netflix\n\n"
                logging.warning("the subreddit should be available on netflix!")
            else:
                answer += "[**Watch on Netflix**](" + netflix_link + ")\n\n"
        except netflix_requester.CustomError as e:
            logging.warning(e)
    else:
        answer += "This episode is not on Netflix yet.\n\n"

    answer += bot_disclaimer
    return answer

# testing:

# print(format_comment("Princess Luna From S2E3 Luna Eclipsed by daisymane","mylittlepony",True))

# print(format_comment("Summoning /u/the_episode_bot arrow s01e03","episode_bot",post=False))
