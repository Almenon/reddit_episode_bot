__author__ = 'Almenon'

#http://praw.readthedocs.org/en/latest/pages/getting_started.html


import praw
import requester
import commentParser
from time import sleep
from json import loads
from json import load
import logging
logging.basicConfig(level="DEBUG")
    # set level to INFO to get rid of debug messages

# SETUP
user_agent = "python script for episode information upon username mention or reply.  alpha v.4 by Almenon"
             # string should not contain keyword bot
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

with open("c:/dev/PycharmProjects/reddit_episode_bot/subreddits.txt",'r') as file:
    subreddit_to_show = load(file) # dictionary [subreddit name] = tv show

bot_disclaimer = "------\n" \
                 "^^I'm ^^a ^^bot ^^that ^^gives ^^info ^^on ^^shows. " \
                 "^^| ^^[message](http://www.reddit.com/message/compose?to=the_episode_bot) ^^me ^^if ^^there's ^^an ^^issue. " \
                 "^^| ^^[about](https://github.com/Almenon/reddit_episode_bot)"
# formatting for bot_disclaimer thanks to wikipediacitationbot

while True:

    try:
        messages = r.get_unread()
    except praw.errors.APIException as e:
        logging.warning("Reddit might be offline: " + str(e))
        sleep(2)
        continue

    for message in messages:
        sleep(2)
        try:
            if message.subreddit in restricted_subreddits:
                r.send_message(message.author, "episodebot could not reply",
                               "episodebot can't reply to a comment in a restricted subreddit")
                continue
            parsedComment = commentParser.parse(message.body)
            show, season, episode = parsedComment
            in_tv_subreddit = False
            if show is None:
                try:
                    show = subreddit_to_show['/r/' + str(message.subreddit)]
                    in_tv_subreddit = True
                except KeyError:
                    r.send_message(message.author, "Please specify a show. If you are in the show's subreddit, "
                                                   "you shouldn't need to specify it. Message /u/almenon to "
                                                   "add the subreddit to the TV-related subreddit database")
                    logging.info("a subreddit was not listed in database")
                    message.mark_as_read()
                    continue
            # todo: search for reddit discussion and put link to first result in comment
            # (limit feature to certain subreddits because
            # it might not return correct result in some subreddits)
            answer = requester.get_info(show, season, episode)
            answer += bot_disclaimer
            try:
                message.reply(answer)
            except Exception as e:
                logging.warning(str(e))
                # possibly 403 error: sub is private or bot is banned from it
        except (commentParser.ParseError, requester.CustomError) as error_msg:
            # send error message to me and commenter
            r.send_message(message.author, "Episodebot could not reply", "Sorry, " + str(error_msg))
            r.send_message("Almenon", "epiosdebot error", str(message) + '\n\n' + str(error_msg))

        message.mark_as_read()

    logging.info("sleeping for 30 seconds")
    sleep(30)  # limit is 2 seconds. 30 is polite time when bot is in alpha

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
