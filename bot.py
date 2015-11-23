__author__ = 'Almenon'

import praw
# http://praw.readthedocs.org
from time import time,sleep,localtime
import comment_formatter
import post_parser
import commentparser
import omdb_requester
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout
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
restricted_subreddits = restricted_subreddits["disallowed"] + \
                        restricted_subreddits["posts-only"] + \
                        restricted_subreddits["permission"]

subreddits = [r.get_subreddit("bojackhorseman"), r.get_subreddit("orangeisthenewblack")]

with open("info/time.txt") as file:
    last_checked = load(file)
num_posts = {
    str(subreddits[0]): 0,
    str(subreddits[1]): 0
}
post_limit = { # limit per day
    str(subreddits[0]): 4,
    str(subreddits[1]): 4
}
last_day = localtime().tm_mday


while True:

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
                    num_posts[str(subreddit)] += 1
                    if num_posts[str(subreddit)] == post_limit[str(subreddit)]:
                        sleep(24-localtime().tm_hour)  # sleep rest of day
                    logging.info("bot commented at " + submission.permalink)
                    print("bot commented at " + submission.permalink)

                except omdb_requester.CustomError as error_msg:
                    # send error message to me
                    r.send_message("Almenon", "epiosdebot error", submission.permalink + '\n\n' + str(error_msg))
                    logging.warning(str(error_msg))
                except post_parser.ParseError as error_msg:
                    logging.warning(str(error_msg))

        last_checked = time()
        # another approach would be to save newest submission id
        # r.get_subreddit("name",place_holder=id) to get content newer than id
        with open("info/time.txt", 'w') as file:
            file.write(str(last_checked))

        # reset post limits each new day
        if localtime().tm_mday != last_day:
            for key in num_posts: num_posts[key] = 0
            last_day = localtime().tm_mday


        for message in messages:
            try:
                print("message: " + message.body)
                if message.subreddit in restricted_subreddits:
                    r.send_message(message.author, "episodebot could not reply",
                                   "episodebot can't reply to a comment in a restricted subreddit")
                    message.mark_as_read()
                    continue
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
                try: # if message is comment reply add link to comment
                    logging.warning(str(error_msg) + '\n' + message.permalink)
                    r.send_message("Almenon", "episodebot error", str(error_msg) + '\n\n' + message.permalink)
                except AttributeError:
                    message_link = "https://www.reddit.com/message/messages/" + message.id
                    logging.warning(str(error_msg) + "\nmessage: " + str(message) + '\n\n' + message_link + str(error_msg))
                    r.send_message("Almenon", "episodebot error", str(message) + '\n\n' + str(error_msg))

            message.mark_as_read()

    except praw.errors.PRAWException as e:
        logging.exception(e)
        last_checked = time()
        with open("info/time.txt", 'w') as file:
            file.write(str(last_checked))
    except (ConnectionError, ReadTimeout) as e:
        print("there was an error connecting to reddit.  Check if it's down or if there is no internet connection")
        logging.exception(e)
        last_checked = time()
        with open("info/time.txt", 'w') as file:
            file.write(str(last_checked))
        sleep(1200)  # sleep for 20 min

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
