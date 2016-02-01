__author__ = 'Almenon'

import praw
# http://praw.readthedocs.org
import comment_formatter
import post_parser
import commentparser
import omdb_requester
from json import loads
import logging

####################  SETUP   ######################
logging.basicConfig(level="INFO",
                    filename="info/bot.log",
                    format='%(asctime)s %(module)s:%(levelname)s: %(message)s'
                    )
# todo: fix logging (it's not logging to the file anymore)
# todo: stop praw debug logs from going to console
logging.info("Bot started")
user_agent = "python script for episode information upon request or activated by keyphrase in participating subreddits." \
             "alpha v1.1 by Almenon"
# string should not contain keyword bot
r = praw.Reddit(user_agent=user_agent)
with open("info/password.txt") as file:
    password = file.read()
    # password in text file so it's not available in public repository
r.login('the_episode_bot', password, disable_warning=True)
# todo: use Oauth instead of login because it will be deprecated in March
# user to send error messages too

bottiquette = r.get_wiki_page('Bottiquette', 'robots_txt_json')
# see https://www.reddit.com/r/Bottiquette/wiki/robots_txt_json
restricted_subreddits = loads(bottiquette.content_md)
restricted_subreddits = restricted_subreddits["disallowed"] + \
                        restricted_subreddits["posts-only"] + \
                        restricted_subreddits["permission"]

subreddits = ["bojackhorseman","orangeisthenewblack","gravityfalls"]
subreddits = [r.get_subreddit(s) for s in subreddits]

num_posts = {}
for s in subreddits:
    num_posts[str(s)] = 0

post_limit = {}
for s in subreddits:
    post_limit[str(s)] = 4

bad_comments = list(range(50))
# store downvoted comments so i don't repeatedly warn myself of the same bad comment

def scan(last_scan):
    """"
    scans replies, mentions, messages, and configured subreddits.
    Replies if keyphrase detected.  Alerts dev if there are any issues.
    :param: last scan time
    :raises: Hopefully nothing, unless there is a connection problem
    """

    global num_posts
    global bad_comments

    for subreddit in subreddits:

        if num_posts[str(subreddit)] >= post_limit[str(subreddit)]:
            continue

        submissions = subreddit.get_new()

        for submission in submissions:
            try:
                if submission.created_utc < last_scan:
                    logging.info("no new posts in " + str(submission.subreddit))
                    break
                logging.info("analyzing " + submission.permalink)
                answer = comment_formatter.format_comment(submission.title, submission.subreddit, post=True)
                submission.add_comment(answer)
                logging.info("bot commented at " + submission.permalink)
                num_posts[str(subreddit)] += 1

            except omdb_requester.CustomError as error_msg:
                logging.warning(str(error_msg))
            except post_parser.ParseError as error_msg:
                logging.warning(str(error_msg))

    # check for summons in replies / messages / mentions
    messages = r.get_unread()
    for message in messages:
        try:
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
        except (commentparser.ParseError, omdb_requester.CustomError) as error_msg:
            # send error message to me and commenter
            try: # if message is comment reply add link to comment
                logging.warning(str(error_msg) + '\n' + message.permalink)
            except AttributeError:
                message_link = "https://www.reddit.com/message/messages/" + message.id
                logging.warning(str(error_msg) + "\nmessage: " + str(message) + '\n\n' + message_link + str(error_msg))

        message.mark_as_read()

    # check if any comments are downvoted
    user = r.get_redditor('the_episode_bot')
    comments = user.get_comments(time='week') # week selector does not work
    for x in comments:
        # dont analyze comments more than a week old
        if x.created_utc<(last_scan-604800):
            break
        if x.id in bad_comments: continue
        if x.score < 0:
            bad_comments.insert(0,x.id)
            bad_comments.pop()
            logging.warning("downvoted comment alert")