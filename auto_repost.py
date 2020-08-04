#! python 3
import praw
import time
import config

reddit = praw.Reddit(
    user_agent='u/' + config.REDDIT_USER + 'v1.0',
    username=config.REDDIT_USER,
    password=config.REDDIT_PASS,
    client_id=config.REDDIT_CLIENT_ID,
    client_secret=config.REDDIT_CLIENT_SECRET
)


def match_flair(value):
    for template in reddit.subreddit(config.MASTER).flair.link_templates:
        flair_text = template['text']
        flair_id = template['id']
        if flair_text == value:
            return flair_id


count_sucessful_link_posts = 1
count_skipped_posts = 1
count_skipped_banned_posts = 1
stored = list()
reddit.validate_on_submit = True
TARGETS_ = "+".join(config.TARGETS)
print(TARGETS_)
print('Posting to', config.MASTER)
while True:
    ## Grab all rising posts
    for s in reddit.subreddit(TARGETS_).rising():
        ## Ignore stickied posts
        if not s.stickied and not s.is_self and s.title not in stored and s.url not in stored and s.domain in config.ALLOWED_DOMAINS:
            ## Allow posts with less score from smaller subs
            if s.subreddit == config.TARGETS[0]: # LSF
                if s.score <= config.SCORE_MAIN:
                    continue
            else:
                if s.score <= config.SCORE_OTHER:
                    continue
            ## Only allow twitch clips from other subs
            if s.subreddit != config.TARGETS[0]: # LSF
                if s.domain != 'clips.twitch.tv':
                    print('SKIP:', count_skipped_posts, ':', s.title)
                    count_skipped_posts += 1
                    stored.append(s.title)
                    continue
            ## skip if banned poster
            if not config.ALLOW_BANNED_AUTHORS:
                if any(reddit.subreddit(config.MASTER).banned(s.author)):
                    print(count_skipped_banned_posts, ': BANNED,', s.title)
                    count_skipped_banned_posts += 1
                    stored.append(s.title)
                    continue
            ## skip if banned flair/word
            if s.flair in config.BANNED_FLAIRS or any(word in s.title for word in config.BANNED_TITLES):
                print(count_skipped_banned_posts, ': BANNED,', s.title)
                count_skipped_banned_posts += 1
                stored.append(s.title)
                continue
            ## Check if post not in stored
            if (s.url not in stored) and (s.title not in stored):
                for i in s.duplicates():
                    if i.subreddit == config.MASTER and i.url == s.url:
                        print('SKIP:', count_skipped_posts, ':', s.title)
                        count_skipped_posts += 1
                        stored.append(s.title)
                        break
                        continue
            ## If loop hasn't been killed and post not in stored, post it
            if (s.url not in stored) and (s.title not in stored):
                ## If link post
                if not s.is_self:
                    try:
                        print(count_sucessful_link_posts, ': Posting', s.title, '(', s.subreddit,')')
                        count_sucessful_link_posts += 1
                        reddit.subreddit(config.MASTER).submit(
                            title=s.title, 
                            flair_id=match_flair(s.flair), 
                            send_replies=False, 
                            url=s.url, 
                            nsfw=s.over_18, 
                            spoiler=s.spoiler,
                            resubmit=False
                        )
                        stored.append(s.url)
                        if s.subreddit == config.TARGETS[0]:
                            time.sleep((config.POST_FREQUENCY * 60))
                        else:
                            time.sleep(((config.POST_FREQUENCY/2) * 60))
                    except:
                        pass
                stored.append(s.title)
            time.sleep(10)