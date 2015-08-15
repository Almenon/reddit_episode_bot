__author__ = 'Almenon'

#http://praw.readthedocs.org/en/latest/pages/getting_started.html


import praw
from time import time
import requester
import netflix_requester
import commentParser
from time import sleep
from json import loads
from json import load
from requests.exceptions import ConnectionError
#import sys
#sys.stderr = open("botlog.txt",'w')
    # disable this when testing
    # make sure to periodically check on log
    # todo: get logging redirect to stderr working
import logging
logging.basicConfig(level="DEBUG",filename="botlog.txt")
    # set level to INFO to get rid of debug messages

# SETUP
user_agent = "python script for episode information upon username mention or reply.  alpha v.5 by Almenon"
             # string should not contain keyword bot
r = praw.Reddit(user_agent=user_agent)
with open("password.txt") as file:
    password = file.read()
    # password in text file so it's not available in public repository
r.login('the_episode_bot', password, disable_warning=True)
    #todo: use Oauth instead of login
    # must be done by this year because login will be deprecated

bottiquette = r.get_wiki_page('Bottiquette', 'robots_txt_json')
# see https://www.reddit.com/r/Bottiquette/wiki/robots_txt_json
restricted_subreddits = loads(bottiquette.content_md)
restricted_subreddits = restricted_subreddits["disallowed"] + restricted_subreddits["posts-only"] + restricted_subreddits["permission"]

subreddit = r.get_subreddit("bojackhorseman")

with open("subreddits.txt") as file:
    subreddit_to_show = load(file) # dictionary [subreddit name] = tv show
with open("time.txt") as file:
    last_checked = load(file)


bot_disclaimer = "------\n" \
                 "^^I'm ^^a ^^bot ^^that ^^gives ^^info ^^on ^^shows. " \
                 "^^| ^^[message](http://www.reddit.com/message/compose?to=the_episode_bot) ^^me ^^if ^^there's ^^an ^^issue. " \
                 "^^| ^^[about](https://github.com/Almenon/reddit_episode_bot)"
# formatting for bot_disclaimer thanks to wikipediacitationbot

while True:

    try:
        messages = r.get_unread()
        submissions = subreddit.get_new()
    except ConnectionError as e:
        logging.warning("Reddit is busy or offline: " + str(e) + "\n sleeping for 10 min")
        #if last_connection_error < 20 min :
        #    sleep(3600) # sleep for hour
        sleep(600) # sleep for 10 min
        continue

    for submission in submissions:
        try:
            if submission.created_utc < last_checked:
                logging.info("no new posts in " + str(submission.subreddit))
                break
            logging.info("analyzing " + submission.permalink + "\n created at utc time " + str(submission.created_utc))
            # parse
            parsedComment = commentParser.parse(submission.title)
            show, season, episode = parsedComment
            # infer show
            if show is None:
                try:
                    show = subreddit_to_show['/r/' + str(submission.subreddit).lower()]
                    # maybe I can find TV show titles by seperating subreddit titles by caps after all
                except KeyError:
                    logging.info("the subreddit is not in subreddits.txt")
                    continue
            # get netflix & imdb link, add on disclaimer
            answer = requester.get_info(show, season, episode)
            netflix_link = netflix_requester.get_netflix_id(show)
            if netflix_link is not None:
                answer += "[**Watch on Netflix**](" + netflix_link + ")\n\n"
            else:
                answer += "Not available on Netflix\n\n"
                logging.warning("bojack should be availible on netflix!")
            answer += bot_disclaimer
            # post
            try:
                submission.add_comment(answer)
            except Exception as error_msg:
                r.send_message("Almenon", "epiosdebot error", str(submission) + '\n\n' + str(error_msg))
                logging.warning(str(error_msg))
                # possibly 403 error: sub is private or bot is banned from it

        except requester.CustomError as error_msg:
            # send error message to me
            r.send_message("Almenon", "epiosdebot error", str(submission) + '\n\n' + str(error_msg))
            logging.warning(str(error_msg))
        except commentParser.ParseError as error_msg:
            logging.warning(str(error_msg))

    last_checked = time()
    # another approach would be to save newest submission id
    # r.get_subreddit("name",place_holder=id) to get content newer than id
    with open("time.txt",'w') as file:
        file.write(str(last_checked))

    for message in messages:
        sleep(2)
        try:
            if message.subreddit in restricted_subreddits:
                r.send_message(message.author, "episodebot could not reply",
                               "episodebot can't reply to a comment in a restricted subreddit")
                message.mark_as_read()
                continue
            #if message.subreddit.description.find(
            #   needs_spoiler = True
            parsedComment = commentParser.parse(message.body)
            show, season, episode = parsedComment
            in_tv_subreddit = False
            if show is None:
                try:
                    show = subreddit_to_show['/r/' + str(message.subreddit).lower()]
                    # maybe I can find TV show titles by seperating subreddit titles by caps after all
                    in_tv_subreddit = True
                except KeyError:
                    r.send_message(message.author, "Please specify a show. If you are in the show's subreddit, "
                                                   "you shouldn't need to specify it. Message /u/almenon to "
                                                   "add the subreddit to the TV-related subreddit database")
                    logging.info("a subreddit was not listed in database")
                    message.mark_as_read()
                    continue

            answer = requester.get_info(show, season, episode)
            netflix_link = netflix_requester.get_netflix_id(show)
            if netflix_link is not None:
                answer += "[**Watch on Netflix**](" + netflix_link + ")\n\n"
            else:
                answer += "Not available on Netflix\n\n"
            answer += bot_disclaimer
            try:
                message.reply(answer)
            except Exception as e:
                r.send_message(message.author, "Episodebot could not reply",
                               "Something went wrong with my bot or your request:\n\n error message: " + str(error_msg))
                r.send_message("Almenon", "epiosdebot error", str(message) + '\n\n' + str(error_msg))
                logging.warning(str(e))
                # possibly 403 error: sub is private or bot is banned from it
        except (commentParser.ParseError, requester.CustomError) as error_msg:
            # send error message to me and commenter
            r.send_message(message.author, "Episodebot could not reply",
                            "Something went wrong with my bot or your request:\n\n error message: " + str(error_msg))
            r.send_message("Almenon", "epiosdebot error", str(message) + '\n\n' + str(error_msg))
            logging.warning(str(error_msg) + "\n comment: " + str(message))

        message.mark_as_read()

    logging.info("sleeping for 120 seconds")
    sleep(120)  # limit is 2 seconds. 30 is polite time when bot is in alpha

"""
LINKS AND NOTES:
https://www.reddit.com/r/television
http://tv-subreddits.wikidot.com/ (TV subreddits masterlist), out of date :(
https://www.reddit.com/r/TVSubreddits/top/ for new TV subreddits

https://github.com/reddit/reddit/wiki/OAuth2
http://praw.readthedocs.org/en/latest/pages/oauth.html

reddit bots & utilities: https://github.com/voussoir/reddit
auto-wiki bot https://github.com/acini/autowikibot-py
can use https://www.reddit.com/r/FreeKarma/ to get free karma if needed
"""
