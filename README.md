# reddit episode bot

### features

When it is mentioned with a season and episode number it will return the title, a summary, release date, and rating.
Additionally, the title links to the imdb page.  Possible features for new version include: Oauth, 
link to discussion thread, search by title, 24/7 online status via cloud-hosting, support for shows with multiple
series (ex: doctor who), and a link to netflix if the show is on it.

### how to activate

You have to mention /u/the_episode_bot or reply to it to active it.  
Currently it is only ran at certain times so it will take a while for the bot to reply, if at all.

Requests should be in a form similar to this:

> "show title" season 3 episode 2. 

Regex parsing allows the bot to accept many different request formats, as well as misspellings. The show title 
can be automatically inferred if the subreddit corresponds to a show in the TV-related subreddits list. 
Note that the listing is out of date, so please message me if there is a new show to include.


Thanks to: [PRAW](https://praw.readthedocs.org/en/v3.1.0/) for conveniently accessing [reddit](https://www.reddit.com/), 
[omdbapi](https://www.omdbapi.com) for providing an open-source tv series database, 
and [TV-related subreddits master-list](http://tv-subreddits.wikidot.com/)
