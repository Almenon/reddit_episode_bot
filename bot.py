__author__ = 'Almenon'

#http://praw.readthedocs.org/en/latest/pages/getting_started.html


import praw
from time import sleep
import requester
import commentParser
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
        sleep(2)
        try:
            if message.subreddit in restricted_subreddits:
                r.send_message(message.author,"episodebot could not reply",
                               "episodebot can't reply to a comment in a restricted subreddit")
                continue
            parsedComment = commentParser.parse(message.body)
            show,season,episode = parsedComment
            if show is None:
                show = "Game of Thrones"
                # todo: use subreddit title as show title
                # just print out subreddit title first to see what I get
                #   use only if show title isn't mentioned in comment
            # todo: search reddit for discussion threads
            # restrict search to current subreddit if it's a show subreddit
            # discussion = r.search(show + ' ' + episode + ' ' + title)
            answer = requester.get_info(show, season, episode)
            answer += bot_disclaimer
            try:
                message.reply(answer)
            except Exception as e:
                logging.warning(str(e))
                # possibly 403 error: sub is private or bot is banned from it
        except (commentParser.ParseError, requester.CustomError) as error_msg:
            # send error message to me and commenter
            #r.send_message(message.author, "Episodebot could not reply", "Sorry, " + error_msg)
            r.send_message("Almenon", "epiosdebot error", str(message) + '\n\n' + error_msg)

        message.mark_as_read()

    logging.info("sleeping for 30 seconds")
    sleep(30) # limit is 2 seconds

"""
LINKS AND NOTES:
for parsing subreddit titles:
    ex: Gameofthrones
    determining where spaces are is a problem
    perhaps I could tell based on capitalization?
    or look in sidebar where hopefully it is mentioned w/ spaces?
perhaps instead of getting list of TV subreddits I could use my own list of TV shows and search for related subreddits?
https://www.reddit.com/r/television
http://tv-subreddits.wikidot.com/ (TV subreddits masterlist, out of date :(
https://www.reddit.com/r/TVSubreddits/top/ for new TV subreddits
https://github.com/reddit/reddit/wiki/OAuth2
http://praw.readthedocs.org/en/latest/pages/oauth.html
use pprint for debugging pprint(vars(submission))
reddit bots & utilities: https://github.com/voussoir/reddit
auto-wiki bot https://github.com/acini/autowikibot-py
can use https://www.reddit.com/r/FreeKarma/ to get free karma if needed
"""
