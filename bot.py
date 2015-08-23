__author__ = 'Almenon'

import praw
# http://praw.readthedocs.org
from time import time
import omdb_requester
import netflix_requester
import commentparser
from requests.exceptions import ConnectionError
from time import sleep
from json import loads, load
import logging

####################  SETUP   ######################
logging.basicConfig(level="INFO",
                    filename="info/bot.log",
                    format='%(asctime)s %(module)s:%(levelname)s: %(message)s'
                    )
logging.info("Bot started")
# set level to INFO to get rid of debug messages
user_agent = "python script for episode information upon username mention or reply.  alpha v.5 by Almenon"
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

with open("info/subreddits.txt") as file:
    subreddit_to_show = load(file) # dictionary [subreddit name] = tv show
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
                    logging.info("analyzing " + submission.permalink + "\n created at utc time " + str(submission.created_utc))
                    print("analyzing " + submission.permalink)
                    # parse
                    parsedComment = commentparser.parse(submission.title)
                    show, season, episode = parsedComment
                    # infer show
                    if show is None:
                        show = subreddit_to_show['/r/' + str(submission.subreddit).lower()]
                    # get netflix & imdb link, add on disclaimer
                    answer = omdb_requester.get_info(show, season, episode)
                    netflix_link = netflix_requester.get_netflix_link(show)
                    if netflix_link is None:
                        answer += "Not available on Netflix\n\n"
                        logging.warning("the subreddit should be availible on netflix!")
                    else:
                        answer += "[**Watch on Netflix**](" + netflix_link + ")\n\n"
                    answer += bot_disclaimer
                    # post
                    submission.add_comment(answer)
                    print("bot commented at " + submission.permalink)

                except omdb_requester.CustomError as error_msg:
                    # send error message to me
                    r.send_message("Almenon", "epiosdebot error", submission.permalink + '\n\n' + str(error_msg))
                    logging.warning(str(error_msg))
                except commentparser.ParseError as error_msg:
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
                parsedComment = commentparser.parse(message.body)
                show, season, episode = parsedComment
                in_tv_subreddit = False
                if show is None:
                    try:
                        show = subreddit_to_show['/r/' + str(message.subreddit).lower()]
                        # maybe I can find TV show titles by seperating subreddit titles by caps after all
                        in_tv_subreddit = True
                    except KeyError:
                        r.send_message(message.author, "Episode bot could not reply",
                                       "Please specify a show. If you are in the show's subreddit, "
                                       "you shouldn't need to specify it. Message /u/almenon to "
                                       "add the subreddit to the TV-related subreddit database")
                        logging.info("a subreddit was not listed in database")
                        message.mark_as_read()
                        continue

                answer = omdb_requester.get_info(show, season, episode)
                netflix_link = netflix_requester.get_netflix_link(show)
                if netflix_link is not None:
                    answer += "[**Watch on Netflix**](" + netflix_link + ")\n\n"
                else:
                    answer += "Not available on Netflix\n\n"
                answer += bot_disclaimer
                message.reply(answer)
                print("bot replied to a comment")
            except (commentparser.ParseError, omdb_requester.CustomError) as error_msg:
                # send error message to me and commenter
                try:
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
    except ConnectionError as e:
        print("there was a connection error")
        logging.warning(e)
        logging.warning(vars(e))
        logging.warning(e._raw.status_code)
        last_checked = time()
        with open("info/time.txt", 'w') as file:
            file.write(str(last_checked))
        sleep(600)  # sleep for 10 min

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
