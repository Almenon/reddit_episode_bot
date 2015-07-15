__author__ = 'Almenon'

#http://praw.readthedocs.org/en/latest/pages/getting_started.html


import praw
from time import sleep
from requester import get_info
import logging
logging.basicConfig(level="DEBUG")
    # set level to INFO to get rid of debug messages
from re import compile, search


# SETUP
# string should not contain keyword bot
user_agent = "Python script for automatic replies with information when my username is tagged with keywords. alpha v.2 by Almenon"
r = praw.Reddit(user_agent=user_agent)


password = open("password.txt").read()
    # password in text file so it's not availible in public repository
r.login('the_episode_bot', password, disable_warning=True)
#todo: use Oauth instead of login
# must be done by this year because login will be deprecated

already_replied = [] # comments already responded too
bot_disclaimer = "------\n" \
                 "^^I'm ^^a ^^bot ^^that ^^gives ^^info ^^on ^^shows. " \
                 "^^| ^^[message](http://www.reddit.com/message/compose?to=the_episode_bot) ^^me ^^if ^^there's ^^an ^^issue. " \
                 "^^| ^^[about](https://github.com/Almenon/reddit_episode_bot)"
# formatting for bot_disclaimer thanks to wikipediacitationbot

while(True):

    messages = r.get_unread()

    for message in messages:
        # todo: only comment on allowed subreddits
        # https://www.reddit.com/r/Bottiquette/wiki/robots_txt_json
        # if message.subreddit is in banned subreddits:
        #   message person
        answer = get_info(str(message.body))
        if answer is not None:
            if answer[0:3] != "400" and answer[0:3] != "404":
                answer += bot_disclaimer
                try:
                    message.reply(answer)
                except Exception as e:
                    logging.error(str(e))
                    # possibly 403 error: sub is private or bot is banned from it
                sleep(2)
                message.mark_as_read()
            else:
                logging.warning("database is offline!")
                message.reply("I can't process your request right now, the database is offline")
                r.send_message("Almenon", "episodebot warning", answer)
        else:
            r.send_message("Almenon", "bad request to episodebot", str(message))
        message.mark_as_read()

    # todo: error handling if reddit is offline
    # should send message to /u/Almenon if an error occurs
    # r.send_message("Almenon", "Episode bot error", "error message")
    logging.debug("sleeping for 30 seconds")
    sleep(30) # limit is 2 seconds

# LINKS:
# https://github.com/reddit/reddit/wiki/OAuth2
# http://praw.readthedocs.org/en/latest/pages/oauth.html
# use pprint for debugging pprint(vars(submission))
# reddit bots & utilities: https://github.com/voussoir/reddit
# auto-wiki bot https://github.com/acini/autowikibot-py
# can use https://www.reddit.com/r/FreeKarma/ to get free karma if needed
