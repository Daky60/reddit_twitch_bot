# Reddit auto moderate twitch-related sub
A reddit bot that;  
auto reposts from other subreddits to another,  
auto moderates posts containing twitch clips,  
attaches vod & mirror links to posts.

## Important
This project served a specific use case not applicable to many others but can be repurposed for different things.  

## auto_mod.py
This code moderates ones subreddit, meaning it will:  
Auto flair, deletes posts with low engagement,  
disallows self promotion, old clips,  
attaches VOD and mirror links.

## auto_repost.py
This code rips posts from desired subreddits which fits specified conditions

## auto_repost_domain.py
This code rips posts from desired domain (e.g. https://www.reddit.com/domain/clips.twitch.tv/) which fits desired conditions.

## Getting started
> Create and fill out config.py (see config_sample.py)

### 1. Install required packages
> pip install -r requirements.txt

### 2. Create an app on Reddit
> See: https://old.reddit.com/prefs/apps/

### 3. Create an account on Streamable
> See: https://streamable.com/signup

### 4. Create an app on Twitch
> See: https://dev.twitch.tv/console/apps