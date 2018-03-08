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

limitedNetflixRelease = {
    # not shows have limited release currently.  if it did i would have a value like: 'mylittlepony': 7.13,
}

spoiler1 = '[{}](/spoiler)'
spoiler2 = '[](#s "{}")'
spoiler3 = '[{}](#spoiler)'
spoiler4 = '[Spoiler Alert](/s "{}")'

spoilers = {
    "bojackhorseman":spoiler2,
    "orangeisthenewblack":spoiler1,
    "gravityfalls":spoiler3,
    "mylittlepony":spoiler1,
    "archerfx":spoiler1,
    "stevenuniverse":spoiler2,
    "blackmirror":spoiler4,
    "episode_bot":spoiler1,
    "shield":spoiler1,
    "preacher":spoiler2
}

hulu_links = {
    "archer":"https://www.hulu.com/archer",
    "preacher":"https://www.hulu.com/preacher"
}

reply = "#####&#009;  \n######&#009;  \n####&#009;  \n" \
         "[**{title}**](http://www.imdb.com/title/{id}) {rating}|" \
         " {watch_link}" \
         "[imdb](http://www.imdb.com/title/{id})" \
         "{plot}"


class NotEnoughInfoError(Exception):
    """
    Raised when post does not have essential info (plot summary or watch link)
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

    season,episode = post_parser.parse(request)
    subreddit = str(subreddit).lower() # clean input
    show = subreddit_to_show[subreddit]
    episode_info = omdb_requester.get_info(show, season, episode)

    if episode_info['Year'].isdigit() and int(episode_info['Year']) > datetime.now().year\
        or subreddit in limitedNetflixRelease and int(season)+int(episode)/100 > limitedNetflixRelease[subreddit]:
        released = False

    watch_link = ''
    if released:
        try:
            if show in hulu_links:
                link = hulu_links[show]
                watch_site = 'Hulu'
            else:
                link = netflix_requester.get_netflix_link(show)
                watch_site = 'Netflix'
            watch_link = "[Watch on "+watch_site+"](" + link + ") | "
        except KeyError as e:
            logging.warning(e)
            missingInfo += 1
    else:
        missingInfo += 1

    plot = episode_info['Plot']
    if plot == "N/A" or plot == '':
        plot = ''
        missingInfo += 1
    else:
        if subreddit in spoilers:
            plot = spoilers[subreddit].format(plot)
        plot = "\n\n> " + plot

    if missingInfo == 2:
        raise NotEnoughInfoError

    if(episode_info['imdbRating'] == 'N/A'):
        rating = ''
    else:
        rating = '[{} ★] '.format(episode_info['imdbRating'])

    return reply.format(
                title = episode_info['Title'],
                id = episode_info['imdbID'],
                rating = rating,
                watch_link = watch_link,
                plot = plot,
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

    show,season,episode = commentparser.parse(request)
    subreddit = str(subreddit).lower() # clean input
    episode_info = omdb_requester.get_info(show, season, episode)
    if show is None:
        try:
            show = subreddit_to_show[subreddit]
        except IndexError:
            raise commentparser.ParseError

    if episode_info['Year'].isdigit() and int(episode_info['Year']) > datetime.now().year\
        or subreddit in limitedNetflixRelease and int(season)+int(episode)/100 > limitedNetflixRelease[subreddit]:
        released = False

    watch_link = ''
    if released:
        try:
            if show in hulu_links:
                link = hulu_links[show]
                watch_site = 'Hulu'
            else:
                link = netflix_requester.get_netflix_link(show)
                watch_site = 'Netflix'
            watch_link = "[Watch on "+watch_site+"](" + link + ") | "
        except KeyError as e:
            logging.warning(e)

    plot = episode_info['Plot']
    if plot == "N/A":
        plot = ''
    else:
        if subreddit in spoilers:
            plot = spoilers[subreddit].format(plot)

    if(episode_info['imdbRating'] == 'N/A'):
        rating = ''
    else:
        rating = '[{}] '.format(episode_info['imdbRating'])

    return reply.format(
                title = episode_info['Title'],
                id = episode_info['imdbID'],
                rating = rating,
                watch_link = watch_link,
                plot = plot,
    )


# testing:

#print(format_post_reply("Hiatus weekly re-watch thread: Season 4 Episode 12 - Call of the Cutie","orangeisthenewblack"))
#print(format_post_reply("Hiatus weekly re-watch thread: Season 1 Episode 12 - Call of the Cutie","gravityfalls"))
#print(format_post_reply("Hiatus weekly re-watch thread: Season 1 Episode 9 - Call of the Cutie","bojackhorseman"))

# print(format_post_reply("Summoning /u/the_episode_bot arrow s01e03","episode_bot",post=False))
