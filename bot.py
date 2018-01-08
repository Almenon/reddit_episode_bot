__author__ = 'Almenon'

import praw
# http://praw.readthedocs.org
import comment_formatter
import post_parser
import commentparser
import omdb_requester
from json import loads
import logging
import OAuth2Util
from os import environ,path

logging.basicConfig(level="INFO",
                    filename="info/bot.log",
                    format='%(asctime)s %(module)s:%(levelname)s: %(message)s'
                    )
# todo: stop praw debug logs from going to console

subreddits = ["archerfx","bojackhorseman","gravityfalls","mylittlepony","stevenuniverse","blackmirror"]

num_posts = {}
for s in subreddits:
    num_posts[str(s)] = 0

post_limit = {}
for s in subreddits:
    post_limit[str(s)] = 4

ignoredUsers = ['AutoModerator','Chaosritter','MeNowDealWithIt']

badComments = []
# store downvoted comments so i don't repeatedly warn myself of the same bad comment

restricted_subreddits = {}


def login(user_agent):
    """"
    Authenticates bot, loads bottiquette, and turns subreddits into praw objects
    """
    global r
    global subreddits
    global restricted_subreddits

    logging.info("Bot started")
    r = praw.Reddit(user_agent=user_agent)

    # heroku is synced w/ github, and passwords should not be on github
    # which is why password file is created with environment variables
    if not path.isfile('oauth.ini'):
        with open("oauth.ini", 'w') as file:
            file.write('[app]\n\
        scope = identity,account,edit,flair,history,privatemessages,read,submit,wikiread\n\
        refreshable = True\n\
        app_key = ' + environ['OAUTH_key'] + '\n\
        app_secret = ' + environ['OAUTH_secret'] + '\n\n\
        [server]\n\
        server_mode = True\n\n\
        [token]\n\
        token=' + environ['token'] + '\n\
        refresh_token=' + environ['refresh_token'] + '\n\
        valid_until=' + environ['valid_until'])

        o = OAuth2Util.OAuth2Util(r, server_mode=True)
        o.refresh(force=True)
    else:
        o = OAuth2Util.OAuth2Util(r)
        o.refresh(force=True)

    bottiquette = r.get_wiki_page('Bottiquette', 'robots_txt_json')
    # see https://www.reddit.com/r/Bottiquette/wiki/robots_txt_json
    restricted_subreddits = loads(bottiquette.content_md)
    restricted_subreddits = restricted_subreddits["disallowed"] + \
                            restricted_subreddits["posts-only"] + \
                            restricted_subreddits["permission"]

    subreddits = [r.get_subreddit(s) for s in subreddits]


def scan(last_scan):
    """"
    scans replies, mentions, messages, and configured subreddits.
    Replies if keyphrase detected.  logs any issues.
    :param: last scan time in unix time
    :raises: Hopefully nothing, unless there is a connection problem
    """
    check_subreddits(last_scan)
    check_unread()


def check_subreddits(last_scan):
    """
    reply to any valid posts in the monitored subreddits
    """
    global num_posts

    for subreddit in subreddits:

        if num_posts[str(subreddit)] >= post_limit[str(subreddit)]: continue

        for submission in subreddit.get_new():
            try:
                if submission.created_utc < last_scan:
                    logging.info("no new posts in " + str(submission.subreddit))
                    break
                if submission.author.name in ignoredUsers:
                    logging.info('ignored ' + submission.author.name)
                    continue
                logging.info("analyzing " + submission.permalink)
                answer = comment_formatter.format_post_reply(submission.title, submission.subreddit)
                submission.add_comment(answer)
                logging.info("bot commented at " + submission.permalink)
                num_posts[str(subreddit)] += 1

            except (post_parser.ParseError,
                    omdb_requester.OmdbError,
                    comment_formatter.NotEnoughInfoError) as error_msg:

                logging.warning(str(error_msg))

            except omdb_requester.OmdbError as error_msg:
                logging.error(str(error_msg))


def check_unread():
    """
    reply to any valid summons in replies / messages / mentions
    """
    for message in r.get_unread():
        try:
            if message.subreddit in restricted_subreddits:
                r.send_message(message.author, "episodebot could not reply",
                               "episodebot can't reply to a comment in a restricted subreddit")
                message.mark_as_read()
                continue
            try:
                answer = comment_formatter.format_comment_reply(message.body, message.subreddit)
            except KeyError:
                r.send_message(message.author, "Episode bot could not reply",
                               "Please specify a show. If you are in the show's subreddit, "
                               "you shouldn't need to specify it. Message /u/almenon to "
                               "add the subreddit to the TV-related subreddit database")
                logging.info("a subreddit was not listed in database")
                message.mark_as_read()
                continue
            message.reply(answer)
        except commentparser.ParseError as error_msg:
            try: # if message is comment reply add link to comment
                logging.warning(str(error_msg) + '\n' + message.permalink)
            except AttributeError:
                message_link = "https://www.reddit.com/message/messages/" + message.id
                logging.warning(str(error_msg) + "\nmessage: " + str(message) + '\n\n' + message_link + str(error_msg))

        except omdb_requester.OmdbError as error_msg:
            try: # if message is comment reply add link to comment
                logging.error(str(error_msg) + '\n' + message.permalink)
            except AttributeError:
                message_link = "https://www.reddit.com/message/messages/" + message.id
                logging.error(str(error_msg) + "\nmessage: " + str(message) + '\n\n' + message_link + str(error_msg))
                
        finally:        
            message.mark_as_read()
