__author__ = 'Caleb'

import logging
from datetime import datetime
from json import load

import commentparser
import netflix_requester
import omdb_requester
import post_parser

with open("info/subreddits.txt") as file:
    subreddit_to_show = load(file)  # dictionary [subreddit name] = tv show
bot_disclaimer = "------\n" \
                 "^^I'm ^^a ^^bot ^^that ^^gives ^^info ^^on ^^shows. " \
                 "^^| ^^[message](http://www.reddit.com/message/compose?to=the_episode_bot) ^^me " \
                 "^^if ^^there's ^^an ^^issue. ^^| ^^[about](https://github.com/Almenon/reddit_episode_bot)"
# formatting for bot_disclaimer thanks to wikipediacitationbot

limitedNetflixRelease = {
    'mylittlepony': 5.26,
}

spoiler1 = '[{}](/spoiler)'
spoiler2 = '[](#s "{}")'
spoiler3 = '[{}](#spoiler)'

spoilers = {
    "bojackhorseman": spoiler2,
    "orangeisthenewblack": spoiler1,
    "gravityfalls": spoiler3,
    "mylittlepony": spoiler1,
    "archerfx": spoiler1
}

postReply = "#####&#009;  \n######&#009;  \n####&#009;  \n" \
            "[**{title}**](http://www.imdb.com/title/{id}) {rating}|" \
            " {netflix}" \
            "[imdb](http://www.imdb.com/title/{id})" \
            "\n\n> {plot}"


class NotEnoughInfoError(Exception):
    """
    Raised when post does not have essential info (plot summary or netflix link)
    Raising this exception ensures that only high quality posts survive
    """
    pass


def format_post_reply(request, subreddit):
    """
    :param request: comment text or post title
    :param subreddit: PRAW subreddit object or name of subreddit (without the /r/)
    :return: a paragraph of info and links about the episode, formatted for Reddit
    :except: omdb_requester.CustomError, post_parser.ParseError, comment_formatter.CustomError
    """
    missingInfo = 0
    released = True

    season, episode = post_parser.parse(request)
    subreddit = str(subreddit).lower()  # clean input
    show = subreddit_to_show[subreddit]
    episode_info = omdb_requester.get_info(show, season, episode)

    if episode_info['Year'].isdigit() and int(episode_info['Year']) > datetime.now().year \
            or subreddit in limitedNetflixRelease and int(season) + int(episode) / 100 > limitedNetflixRelease[
                subreddit]:
        released = False

    netflix = ''
    if released:
        try:
            netflix_link = netflix_requester.get_netflix_link(show)
            if netflix_link is None:
                missingInfo += 1
                logging.warning('netflix link is None')
            else:
                netflix = f"[Watch on Netflix]({netflix_link}) | "
        except netflix_requester.CustomError as e:
            logging.warning(e)
            missingInfo += 1
    else:
        missingInfo += 1

    plot = episode_info['Plot']
    if plot == "N/A":
        plot = ''
        missingInfo += 1
    else:
        if subreddit in spoilers:
            plot = spoilers[subreddit].format(plot)

    if missingInfo == 2:
        raise NotEnoughInfoError

    if episode_info['imdbRating'] == 'N/A':
        rating = ''
    else:
        rating = f"[{episode_info['imdbRating']}] "  # the space at end is important

    return postReply.format(
        title=episode_info['Title'],
        id=episode_info['imdbID'],
        rating=rating,
        netflix=netflix,
        plot=plot,
    )


def format_comment_reply(request, subreddit):
    """
    unlike format post reply, this formatter is more lenient if there's missing data

    :param request: comment text or post title
    :param subreddit: PRAW subreddit object or name of subreddit (without the /r/)
    :return: a paragraph of info and links about the episode, formatted for Reddit
    :except: omdb_requester.CustomError, commentparser.ParseError
    """

    global subreddit_to_show
    global bot_disclaimer
    released = True

    show, season, episode = commentparser.parse(request)
    subreddit = str(subreddit).lower()  # clean input
    episode_info = omdb_requester.get_info(show, season, episode)
    if show is None:
        try:
            show = subreddit_to_show[subreddit]
        except IndexError:
            raise commentparser.ParseError

    if episode_info['Year'].isdigit() and int(episode_info['Year']) > datetime.now().year \
            or subreddit in limitedNetflixRelease and int(season) + int(episode) / 100 > limitedNetflixRelease[
                subreddit]:
        released = False

    netflix = ''
    if released:
        try:
            netflix_link = netflix_requester.get_netflix_link(show)
            if netflix_link is None:
                logging.warning('netflix link is None')
            else:
                netflix = f"[Watch on Netflix]({netflix_link}) | "
        except netflix_requester.CustomError as e:
            logging.warning(e)

    plot = episode_info['Plot']
    if plot == "N/A":
        plot = ''
    else:
        if subreddit in spoilers:
            plot = spoilers[subreddit].format(plot)

    if episode_info['imdbRating'] == 'N/A':
        rating = ''
    else:
        rating = f"[{episode_info['imdbRating']}] "  # the space at end is important

    return postReply.format(
        title=episode_info['Title'],
        id=episode_info['imdbID'],
        rating=rating,
        netflix=netflix,
        plot=plot,
    )

# testing:

# print(format_post_reply("Hiatus weekly re-watch thread: Season 4 Episode 12 - Call of the Cutie","orangeisthenewblack"))
# print(format_post_reply("Hiatus weekly re-watch thread: Season 1 Episode 12 - Call of the Cutie","gravityfalls"))
# print(format_post_reply("Hiatus weekly re-watch thread: Season 1 Episode 9 - Call of the Cutie","bojackhorseman"))

# print(format_post_reply("Summoning /u/the_episode_bot arrow s01e03","episode_bot",post=False))
