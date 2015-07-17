__author__ = 'Almenon'

#http://praw.readthedocs.org/en/latest/pages/getting_started.html


import praw
from time import sleep
from requester import get_info
import logging
logging.basicConfig(level="DEBUG")
    # set level to INFO to get rid of debug messages
from json import loads

# SETUP
# string should not contain keyword bot
user_agent = "python script for episode information upon username mention or reply.  alpha v.3 by Almenon"
r = praw.Reddit(user_agent=user_agent)

password = open("password.txt").read()
    # password in text file so it's not availible in public repository
r.login('the_episode_bot', password, disable_warning=True)
#todo: use Oauth instead of login
# must be done by this year because login will be deprecated

bottiquette = r.get_wiki_page('Bottiquette', 'robots_txt_json')
# see https://www.reddit.com/r/Bottiquette/wiki/robots_txt_json
restricted_subreddits = loads(bottiquette.content_md)
restricted_subreddits = restricted_subreddits["disallowed"] + restricted_subreddits["posts-only"] + restricted_subreddits["permission"]

bot_disclaimer = "------\n" \
                 "^^I'm ^^a ^^bot ^^that ^^gives ^^info ^^on ^^shows. " \
                 "^^| ^^[message](http://www.reddit.com/message/compose?to=the_episode_bot) ^^me ^^if ^^there's ^^an ^^issue. " \
                 "^^| ^^[about](https://github.com/Almenon/reddit_episode_bot)"
# formatting for bot_disclaimer thanks to wikipediacitationbot

while(True):

    try:
        messages = r.get_unread()
    except praw.errors.APIException as e:
        logging.warning("Reddit might be offline: " + e)
        sleep(2)
        continue

    for message in messages:
        if message.subreddit in restricted_subreddits:
            r.send_message(message.author,"episodebot could not reply",
                           "episodebot can't reply to a comment in a restricted subreddit")
            continue
        answer = get_info(str(message.body))
        # todo: search reddit for discussion threads
        if answer is not None:
            if answer[0:3] != "400" and answer[0:3] != "404":
                answer += bot_disclaimer
                try:
                    message.reply(answer)
                except Exception as e:
                    logging.warning(str(e))
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
