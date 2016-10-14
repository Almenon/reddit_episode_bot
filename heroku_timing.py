__author__ = 'Almenon'

import praw
# http://praw.readthedocs.org
from time import time,sleep,localtime
import bot
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout
import logging
from pymongo import MongoClient
from os import environ

client = MongoClient(environ['mongodb_uri'])
db = client.heroku_m17k26m5
saved_time = db.last_time # type: collection
last_time = saved_time.find_one()['time']

last_day = localtime().tm_mday
bot.login("Python:episodeInfo:v2.0 (by /u/Almenon)")

while True:
    try:
        # scan posts / mentions / messages / replies
        bot.scan(last_time)

        # save time
        last_time = time()
        saved_time.update_one({},{'$set':{'time':last_time}})

        # reset post limits each new day
        if localtime().tm_mday != last_day:
            for key in bot.num_posts: bot.num_posts[key] = 0
            last_day = localtime().tm_mday

    except praw.errors.PRAWException as e:
        logging.exception(e)
        last_time = time()
        saved_time.update_one({},{'$set':{'time':last_time}})
        sleep(180)
    except (ConnectionError, ReadTimeout) as e:
        print("there was an error connecting to reddit.  Check if it's down or if there is no internet connection")
        logging.exception(e)
        last_time = time()
        saved_time.update_one({},{'$set':{'time':last_time}})
        sleep(1200)  # sleep for 20 min

    logging.info("sleeping for 3 minutes")
    print("sleeping")
    sleep(180)  # limit is 2 seconds. 30 is polite time.