__author__ = 'Almenon'

#http://praw.readthedocs.org/en/latest/pages/getting_started.html

import praw
# import OAuth2Util
    # library that makes it easier to use OAuth
    # https://github.com/SmBe19/praw-OAuth2Util
    # todo: use OAuth instead of login
from time import sleep
from requester import input
# import webbrowser # only needed if i use standard Oauth
import logging
logging.basicConfig(level="DEBUG")
    # set level to INFO to get rid of debug messages
from re import compile, search

# SETUP
# string should not contain keyword bot
user_agent = "Python script for automated replies when my username is tagged. alpha v.1 by Almenon"
r = praw.Reddit(user_agent=user_agent)
#o = OAuth2Util.OAuth2Util(r)

r.login('Almenon','password goes here',disable_warning=True) # login will be deprecated soon!
already_replied = [] # comments already responded too
number_responses = 0

while(True):

    mentions = r.get_mentions()

    for mention in mentions:
        # todo: find a way to distinguish between old and new replies
        if mention.new is False: # has_fetched or new
            break
        answer = input(str(mention))
        if answer is not None:
            mention.reply(answer)
        already_replied.append(mention.id)
        logging.debug(vars(mention))

    # for use once episodebot has it's own account
    # unread_messages = r.get_unread()
    # for message in unread_messages:
    #     r.send_message("Almenon", "episodebot", message)

    # # once 55 min has passed update hourly access token
    # last_time = time()
    # if time() > 3300 + last_time:
    #   o.refresh()

    # todo: error handling
    # should send message to /u/Almenon if an error occurs
    # r.send_message("Almenon", "Episode bot error", "error message")
    logging.debug("sleeping for 30 seconds")
    sleep(30) # limit is 2 seconds


# use OAuth to authenticate bot
# https://github.com/reddit/reddit/wiki/OAuth2
# http://praw.readthedocs.org/en/latest/pages/oauth.html
# use pprint for debugging pprint(vars(submission))
# reddit bots & utilities: https://github.com/voussoir/reddit
# auto-wiki bot https://github.com/acini/autowikibot-py
# can use https://www.reddit.com/r/FreeKarma/ to get free karma if needed

# OLD CODE
"""

r.set_oauth_app_info(client_id='',
                    client_secret='',
                     redirect_uri='')
url = r.get_authorize_url("almenon51", "identity privatemessages submit", refreshable=True)
# edit read history flair save are some more permissions i might need
webbrowser.open(url)
sleep(30) # stop program and update below line
access_information = r.get_access_information('') # only lasts 60 min
user = r.get_me()
logging.debug(user.name, user.link_karma)
r.login('Almenon','password') # login will be deprecated soon!

    last_time = time()
    if time() > 3300 + last_time:
        access_information = r.refresh_access_information(access_information['refresh_token'])

subreddit = r.get_subreddit('bottest') #'subreddit1 + subreddit2' if multiple
subreddit_comments = subreddit.get_comments()
# subreddit_comments is a generator
logging.debug(subreddit_comments)

for submission in subreddit.get_hot(limit=10):
    flat_comments = praw.helpers.flatten_tree(submission.comments)
    for comment in flat_comments:
        if comment.body.find("episodebot") and comment.id not in already_replied
            comment.reply("message")
            already_replied.add(comment.id)
            number_responses = number_responses + 1
    #user_name = "Almenon"
#user = r.get_redditor(user_name)
"""