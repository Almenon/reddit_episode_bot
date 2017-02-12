__author__ = 'Almenon'

import logging
from json import load
from time import time, sleep, localtime

from praw.exceptions import PRAWException
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout

import bot

last_day = localtime().tm_mday
with open("info/time.txt") as file:
    last_scan = load(file)


def save_scan_time():
    global last_scan
    last_scan = time()
    with open("info/time.txt", 'w') as file:
        file.write(str(last_scan))
        # another approach would be to save newest submission id
        # r.get_subreddit("name",place_holder=id) to get content newer than id


bot.login("Python:episodeInfo:v2.1 (by /u/Almenon)")

while True:
    try:
        # scan posts / mentions / messages / replies
        bot.scan(last_scan)
        save_scan_time()

        # reset post limits each new day
        if localtime().tm_mday != last_day:
            for key in bot.num_posts: bot.num_posts[key] = 0
            last_day = localtime().tm_mday

    except PRAWException as e:
        logging.exception(e)
        save_scan_time()
        sleep(180)
    except (ConnectionError, ReadTimeout) as e:
        logging.exception(e)
        logging.info(
            "there was an error connecting to reddit.  Check if it's down or if there is no internet connection")
        save_scan_time()
        sleep(1200)  # sleep for 20 min

    logging.info("sleeping for 3 minutes")
    sleep(180)  # limit is 2 seconds. 30 is polite time.
