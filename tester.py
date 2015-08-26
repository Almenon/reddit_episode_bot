import omdb_requester
import praw
from re import compile,search
from time import time
from time import sleep
from json import load
import logging
import pprint
import commentparser
logging.basicConfig(level="DEBUG")

# REQUESTER TEST
# print(requester.get_info("ignore this text, capture s04e02, and ignore this text too"))

# BOT TEST
# replies to a specific comment
# useful for when it doesn't reply to a comment due to an error
# note that it doesn't get the edited versions of a comment, only the original


# setup
user_agent = "python script for episode information upon username mention or reply.  alpha v.3 by Almenon"
r = praw.Reddit(user_agent=user_agent)
password = open("info/password.txt").read()
r.login('the_episode_bot', password, disable_warning=True)
bot_disclaimer = "------\n" \
                     "^^I'm ^^a ^^bot ^^that ^^gives ^^info ^^on ^^shows. " \
                     "^^| ^^[message](http://www.reddit.com/message/compose?to=the_episode_bot) ^^me ^^if ^^there's ^^an ^^issue. " \
                     "^^| ^^[about](https://github.com/Almenon/reddit_episode_bot)"


messages = next(r.get_subreddit('bottest').get_new())
pprint.pprint(vars(messages))



#  ERROR TESTING
# try:
#     subreddit = r.get_subreddit("admin")
#     submissions = subreddit.get_new()
#     print(next(submissions))
#
# except praw.errors.PRAWException as e:
#     print("an error happened")
#     logging.warning(e)
#     print(vars(e)) # until the errors have messages this will have to do
#     try:
#         logging.warning("HTTP error code: " + str(e._raw.status_code))
#     except AttributeError:
#         pass
# sleep(1000)

"Discussions search"
# message = {}
# subreddit = "rickandmorty"
# discussion = r.search("crtyddrgdrgdrgrdgyrsion")
# # print(vars(next(discussion)))
# print(discussion)
# print(next(discussion))


"title response"
    # actually just do
    # unread_posts = [x for x in posts if x.created_utc > time]
    # time = unread_posts[0].created_utc
    # for post in unread_posts[1:]:
    #   # do stuff
    #   # if error, save post # and start loop at post# +1
# a good method would be able to get later posts that encountered an error
# with open("time.txt") as file:
#     last_checked = load(file)
# subreddit = r.get_subreddit("bojackhorseman")
# for submission in subreddit.get_new():
#     try:
#         if submission.created_utc < last_checked:
#             break
#         print(str(submission.created_utc))
#         logging.info("analyzing " + submission.permalink)
#         # parse the comment
#         # sleep after making a comment
#     except commentParser.ParseError as e:
#         print(str(e))
#
# last_checked = time()
# with open("time.txt",'w') as file:
#     file.write(str(last_checked))

"automatic spoiler recognition"
# regex = compile(r"\(([/#]s[^\)]*)")  # (#/s... stops at )
# #spoilers = ("#s","/s","/sp","/spoiler","#spoiler")
#     # might be best to use above - regex accepts to much possibilities
#     # if above is used make sure to arrange words into proper order
# #message = next(r.get_mentions())
# subreddit = r.get_subreddit("orangeisthenewblack")
# sidebar = subreddit.description
# try:
#     print(sidebar)
# except UnicodeEncodeError:
#     logging.info("sidebar has an unrecognizable character - sidebar could not be printed")
#     # occurs with /r/orangeisthenewblack
      # skip the summary and just have link to imdb page? nah... summary is not descriptive, they know what they
# spoiler = search(regex,sidebar)
# #for x in spoilers:
# #    if x in sidebar:
# #       spoiler = x
# #       break
# if spoiler is not None:
#     spoiler = spoiler.group(1)
#     if '"' in spoiler:
#         logging.info("subreddit uses [](spoiler code \"text\") format")
#         spoiler = spoiler.split('"')[0]
#     logging.info("spoiler code is " + spoiler)



"Wiki of subreddit"
# subreddit = r.get_subreddit("raising")
# print(vars(subreddit))
# wiki = r.get_wiki_page("television","index")
# content = wiki.content_md

"episode bot reply to comment"
# # find message id by looking through https://api.reddit.com/message/messages/
   # actually, above is just for messages, not comments, so ignore.
# try:
#     parsedComment = commentParser.parse(message.body)
#     show,season,episode = parsedComment
#     if show is None:
#         show = "Game of Thrones"
#     answer = requester.get_info(show, season, episode)
#     answer += bot_disclaimer
#     try:
#         message.reply(answer)
#     except Exception as e:
#         logging.warning(str(e))
#         # possibly 403 error: sub is private or bot is banned from it
# except (commentParser.CustomError, requester.CustomError) as error_msg:
#     print(error_msg)