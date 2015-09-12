__author__ = 'Almenon'

import praw
# http://praw.readthedocs.org
from time import time
import comment_formatter
import postParser
import commentparser
import omdb_requester
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout
from time import sleep
from json import loads, load
import logging

####################  SETUP   ######################
logging.basicConfig(level="INFO",
                    filename="info/bot.log",
                    format='%(asctime)s %(module)s:%(levelname)s: %(message)s'
                    )
# todo: fix logging (it's not logging to the file anywhere!)
logging.info("Bot started")
# set level to INFO to get rid of debug messages
user_agent = "python script for episode information upon username mention or reply.  alpha v1.1 by Almenon"
# string should not contain keyword bot
r = praw.Reddit(user_agent=user_agent)
with open("info/password.txt") as file:
    password = file.read()
    # password in text file so it's not available in public repository
r.login('the_episode_bot', password, disable_warning=True)
# todo: use Oauth instead of login because it will be deprecated soon

bottiquette = r.get_wiki_page('Bottiquette', 'robots_txt_json')
# see https://www.reddit.com/r/Bottiquette/wiki/robots_txt_json
restricted_subreddits = loads(bottiquette.content_md)
restricted_subreddits = restricted_subreddits["disallowed"] + restricted_subreddits["posts-only"] + restricted_subreddits["permission"]

subreddits = [r.get_subreddit("arrow"), r.get_subreddit("bojackhorseman"), r.get_subreddit("orangeisthenewblack")]

with open("info/time.txt") as file:
    last_checked = load(file)


bot_disclaimer = "------\n" \
                 "^^I'm ^^a ^^bot ^^that ^^gives ^^info ^^on ^^shows. " \
                 "^^| ^^[message](http://www.reddit.com/message/compose?to=the_episode_bot) ^^me ^^if ^^there's ^^an ^^issue. " \
                 "^^| ^^[about](https://github.com/Almenon/reddit_episode_bot)"
# formatting for bot_disclaimer thanks to wikipediacitationbot

# todo:  try to avoid repeating code in post-checking and comment-checking
# problem is their code is slightly different:
# comment errors send message to both author and me, instead of just me
# comment uses .reply rather than .add_comment

while True:

    # see https://www.reddit.com/r/redditdev/comments/3h3hmm
    try:
        messages = r.get_unread()

        for subreddit in subreddits:

            submissions = subreddit.get_new()

            for submission in submissions:
                try:
                    if submission.created_utc < last_checked:
                        logging.info("no new posts in " + str(submission.subreddit))
                        break
                    logging.info("analyzing " + submission.permalink)
                    print("analyzing " + submission.permalink)
                    answer = comment_formatter.format_comment(submission.title, submission.subreddit, post=True)
                    submission.add_comment(answer)
                    logging.info("bot commented at " + submission.permalink)
                    print("bot commented at " + submission.permalink)

                except omdb_requester.CustomError as error_msg:
                    # send error message to me
                    r.send_message("Almenon", "epiosdebot error", submission.permalink + '\n\n' + str(error_msg))
                    logging.warning(str(error_msg))
                except postParser.ParseError as error_msg:
                    logging.warning(str(error_msg))

        last_checked = time()
        # another approach would be to save newest submission id
        # r.get_subreddit("name",place_holder=id) to get content newer than id
        with open("info/time.txt", 'w') as file:
            file.write(str(last_checked))

        for message in messages:
            sleep(2)
            try:
                print("message: " + message.body)
                if message.subreddit in restricted_subreddits:
                    r.send_message(message.author, "episodebot could not reply",
                                   "episodebot can't reply to a comment in a restricted subreddit")
                    message.mark_as_read()
                    continue
                # if message.subreddit.description.find(
                #   needs_spoiler = True
                try:
                    answer = comment_formatter.format_comment(message.body, message.subreddit, post=False)
                except KeyError:
                    r.send_message(message.author, "Episode bot could not reply",
                                   "Please specify a show. If you are in the show's subreddit, "
                                   "you shouldn't need to specify it. Message /u/almenon to "
                                   "add the subreddit to the TV-related subreddit database")
                    logging.info("a subreddit was not listed in database")
                    message.mark_as_read()
                    continue
                message.reply(answer)
                print("bot replied to a comment")
            except (commentparser.ParseError, omdb_requester.CustomError) as error_msg:
                # send error message to me and commenter
                try:
                    # todo: figure out why messages never have a link attached to them
                    logging.warning(str(error_msg) + '\n' + message.link_url+message.id)
                    r.send_message("Almenon", "episodebot error", message.link_url+message.id + '\n\n' + str(error_msg))
                except AttributeError:
                    logging.warning(str(error_msg) + "\nmessage: " + str(message))
                    r.send_message("Almenon", "episodebot error", str(message) + '\n\n' + str(error_msg))

            message.mark_as_read()

    # todo: use logging.exception?
    except praw.errors.PRAWException as e:
        logging.warning(e)  # nothing will be printed: https://github.com/praw-dev/praw/issues/491
        logging.warning(vars(e))  # temporary workaround
        last_checked = time()
        with open("info/time.txt", 'w') as file:
            file.write(str(last_checked))
        try:
            logging.warning("HTTP error code: " + str(e._raw.status_code))
        except AttributeError:
            pass
    except (ConnectionError, ReadTimeout) as e:
        print("there was an error connecting to reddit.  Check if it's down or if there is no internet connection")
        logging.warning(e)
        # logging.warning(vars(e))  # {'response': None, 'request': <PreparedRequest [GET]>}
        # logging.warning(e._raw.status_code)  # todo: find out why this doesn't work (low importance)
        last_checked = time()
        with open("info/time.txt", 'w') as file:
            file.write(str(last_checked))
        sleep(1200)  # sleep for 20 min
    # todo: catch error if internet connection goes offline http://stackoverflow.com/questions/22851609/python-errno-11001-getaddrinfo-failed
    # requests.exceptions.ConnectionError: ('Connection aborted.', gaierror(11001, 'getaddrinfo failed'))

    logging.info("sleeping for 3 minutes")
    print("sleeping")
    sleep(180)  # limit is 2 seconds. 30 is polite time.


"""
LINKS AND NOTES:

for finding subreddits:
https://www.reddit.com/r/television
http://tv-subreddits.wikidot.com/ (TV subreddits masterlist)
    out of date but still comprehensive
https://www.reddit.com/r/TVSubreddits/top/ for new TV subreddits
subreddits should be compatible with omdb and netflixroulette API

OAuth Links:
https://github.com/reddit/reddit/wiki/OAuth2
http://praw.readthedocs.org/en/latest/pages/oauth.html

reddit bots & utilities: https://github.com/voussoir/reddit
auto-wiki bot https://github.com/acini/autowikibot-py
"""
