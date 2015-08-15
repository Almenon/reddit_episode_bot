# Reddit episode bot

A script that provides info and links to TV episodes.  It can automatically create a comment like below:

> ###[Brand New Couch](http://www.imdb.com/title/tt4311472)

> Plot: Picking up where he left off, Bojack Horseman is now set to start filming his dream movie Secretariat.

> imdbRating: 8.4

> Released: 17 Jul 2015

> [**Watch on Netflix**](http://www.netflix.com/title/70300800)

> <sup>I'm a bot that gives info on shows. | [message](http://www.reddit.com/message/compose?to=the_episode_bot) me 
if there's an issue. | [about](https://github.com/Almenon/reddit_episode_bot)


### How to activate

You have to mention, reply, or message /u/the_episode_bot.
Automatic activation when there is a post with the correct format. (currently limited to participating subreddits)
Currently it is only run at certain times so it will take a while for the bot to reply, if at all.

Requests should be in a form similar to this:

> "show title" season 3 episode 2. 

Regex parsing allows the bot to accept many different request formats, as well as misspellings. The show title 
can be automatically inferred if the subreddit corresponds to a show in the TV-related subreddits list. 
Note that the listing is out of date, so please message me if there is a new show to include.  Also, the bot
can't distinguish between different series of the same TV show.  Sorry Doctor Who fans, you are out of luck.

### Possible Upcoming features

* login via Oauth (should arrive soon)
* plot hiding by if a spoiler format is mentioned in the sidebar
* search by episode title 
* 24/7 online status via cloud-hosting 
* support for shows with multiple series 

### Thanks to

* [PRAW](https://praw.readthedocs.org/en/v3.1.0/) for conveniently accessing [reddit](https://www.reddit.com/), 
* [omdbapi](https://www.omdbapi.com) for providing an open-source tv series database, 
* [TV-related subreddits master-list](http://tv-subreddits.wikidot.com/)
* [Netflix Roulette API](http://netflixroulette.net/api/) for links to watch on Netflix

Contributions and constructive criticism are welcomed.