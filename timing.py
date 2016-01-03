__author__ = 'Almenon'

import praw
# http://praw.readthedocs.org
from time import time,sleep,localtime
import bot
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout
from json import load
import logging

last_day = localtime().tm_mday
with open("info/time.txt") as file:
    last_checked = load(file)

while True:
    try:
        # scan posts / mentions / messages / replies
        bot.scan(last_checked)

        # save time
        last_checked = time()
        # another approach would be to save newest submission id
        # r.get_subreddit("name",place_holder=id) to get content newer than id
        with open("info/time.txt", 'w') as file:
            file.write(str(last_checked))

        # reset post limits each new day
        if localtime().tm_mday != last_day:
            for key in bot.num_posts: bot.num_posts[key] = 0
            last_day = localtime().tm_mday

    except praw.errors.PRAWException as e:
        logging.exception(e)
        bot.last_checked = time()
        with open("info/time.txt", 'w') as file:
            file.write(str(last_checked))
        sleep(180)
    except (ConnectionError, ReadTimeout) as e:
        print("there was an error connecting to reddit.  Check if it's down or if there is no internet connection")
        logging.exception(e)
        bot.last_checked = time()
        with open("info/time.txt", 'w') as file:
            file.write(str(last_checked))
        sleep(1200)  # sleep for 20 min

    logging.info("sleeping for 3 minutes")
    print("sleeping")
    sleep(180)  # limit is 2 seconds. 30 is polite time.