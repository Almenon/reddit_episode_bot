# Reddit episode bot

A script that provides info and links to TV episodes.  It can automatically create a comment like below:

> ###[Brand New Couch](http://www.imdb.com/title/tt4311472) [8.4] | [**Watch on Netflix**](http://www.netflix.com/title/70300800) | [Imdb](http://www.imdb.com/title/tt4311472)

> > Picking up where he left off, Bojack Horseman is now set to start filming his dream movie Secretariat.

> > *(Summary text is covered by spoilertag until mouseover)*


### How to activate

You have to mention, reply, or message [/u/the_episode_bot](www.reddit.com/u/the_episode_bot).  If you post a thread with the correct format in the title it automatically activates. (currently limited to participating subreddits\*).  The bot runs during the day and sleeps during the night (Pacific Time)

Requests should be in a form similar to this:

> /u/the_episode_bot Simpsons season 3 episode 2. 

Regex parsing allows the bot to accept many different request formats, as well as misspellings. The show title 
can be automatically inferred if the subreddit corresponds to a show in the TV-related subreddits list. 
Note that the listing is out of date, so please message me if there is a new show to include.  Also, the bot
can't distinguish between different series of the same TV show.  Sorry Doctor Who fans, you are out of luck.

### Thanks to

* [PRAW](https://praw.readthedocs.org/en/v3.1.0/) for conveniently accessing [reddit](https://www.reddit.com/), 
* [omdbapi](https://www.omdbapi.com) for providing an open-source tv series database, 
* [TV-related subreddits master-list](http://tv-subreddits.wikidot.com/)
* [Netflix Roulette API](http://netflixroulette.net/api/) for links to watch on Netflix
* [praw-OAuth2Util](https://github.com/SmBe19/praw-OAuth2Util) for making OAUTH a breeze

Contributions and constructive criticism are welcomed.


[comment]: # (describe how to run a custom version of the bot)
