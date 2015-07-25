# reddit episode bot
When it is mentioned with a season and episode number it will return the title, a summary, release date, and rating.
Still in progress.  Requests should have parameters "show title" episode X season X.

> Possible requests include, but are not limited to:

> "show title" season 1 episode 2

> "show title" s1e2

> "show title" S01E02
  
Of course, you either have to mention /u/the_episode_bot or reply to it to active it.  Currently it is only ran at certain times so it will take a while for the bot to reply, if at all.

Thanks to: [PRAW](https://praw.readthedocs.org/en/v3.1.0/) for conveniently accessing [reddit](https://www.reddit.com/), 
and [omdbapi](https://www.omdbapi.com) for providing an open-source tv series database.
