#! python 3
import praw
import requests
import json
from datetime import datetime, timedelta
import pytz
import dateutil.parser
#import logging; logging.basicConfig(level=logging.DEBUG)

from config import REDDIT_PASS, REDDIT_USER
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET
from config import STREAMABLE_USER, STREAMABLE_PASS
from config import MASTER, TWITCH_SECRET
from config import OFFLINE_TV, DELETE_BAD_AFTER
from config import SKIP_BAD_DELETE_AFTER, DELETE_OLD_CLIP

reddit = praw.Reddit(
    user_agent='u/' + REDDIT_USER + 'v1.0',
    username=REDDIT_USER,
    password=REDDIT_PASS,
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET
)


class auto_moderate:
    def __init__(self, submission):
        self.subreddit = MASTER
        self.submission = submission
        ## special exception because no api support
        self.team_offlinetv = OFFLINE_TV
        self.twitch_api_url = 'https://api.twitch.tv/kraken'
        self.headers = {
            'Client-ID' : TWITCH_SECRET,
            'Accept': 'application/vnd.twitchtv.v5+json'
        }
    ## Request data from twitch
    def request_data(self, endpoint, url):
        requested_url = self.twitch_api_url + '/' + endpoint + '/' + url
        r = requests.get(url=requested_url, headers=self.headers)
        if r.status_code == 200:
            try:
                twitch_data = json.loads(r.text)
                return twitch_data
            except:
                return None
        return None
    def twitch_timestamp(self, timestamp):
        ts = dateutil.parser.parse(timestamp)
        ts = ts.astimezone(pytz.timezone('UTC'))
        ts = ts.replace(tzinfo = None)
        return ts
    def attach_message(self, msg, sticky=None, remove=None):
        comment = self.submission.reply(msg + '\n\n___\n\nPlease contact the moderators of this subreddit if you have any questions or concerns.')
        if sticky:
            comment.mod.distinguish(sticky=True)
        if remove:
            self.submission.mod.remove()
        print(self.submission.title, 'removed: ',' '.join(msg.split()[-2:]))
    ## Removes boring posts
    def low_engagement(self):
        try:
            min_age = datetime.utcnow() - timedelta(hours=DELETE_BAD_AFTER)
            max_age = datetime.utcnow() - timedelta(hours=SKIP_BAD_DELETE_AFTER)
            post_age = datetime.utcfromtimestamp(self.submission.created_utc)
            if self.submission.score <= 2 and self.submission.num_comments <= 3 and post_age <= min_age and not post_age <= max_age:
                self.attach_message('This post has automatically been deleted because of low engagement.', sticky=True, remove=True)
                return skip
        except:
            pass
    def sort_flair(self, name, game):
        ## special exception because no api support
        for template in reddit.subreddit(self.subreddit).flair.link_templates:
            try:
                flair_text = template['text']
                if name in flair_text or flair_text in game:
                    return template['id']
                if game in flair_text or flair_text in game:
                    return template['id']
            except:
                pass
        #return None
    def handle_twitch_clip(self):
        if self.submission.domain == 'clips.twitch.tv':
            proceed = True
            try:
                trim_url = self.submission.url.split('clips.twitch.tv/')[1]
                clip_data = self.request_data('clips', trim_url)
                clip_stream = clip_data['broadcaster']['display_name']
                clip_by = clip_data['curator']['display_name']
                clip_game = clip_data['game']
                clip_created = clip_data['created_at']
                ## Check if self promotion
                if clip_stream == clip_by and proceed:
                    self.attach_message('This post has automatically been deleted because of self promotion.', sticky=True, remove=True)
                    proceed = False
                ## Check if old clip
                if proceed:
                    twitch_ts = self.twitch_timestamp(clip_created) + timedelta(days=DELETE_OLD_CLIP)
                    today = datetime.utcnow()
                    if today > twitch_ts:
                        self.attach_message('This post has automatically been deleted because the clip is more than 30 days old.', sticky=True, remove=True)
                        proceed = False
                ## Check if no flair
                sub_flair = self.submission.link_flair_text
                if sub_flair is None and proceed:
                    set_flair = self.sort_flair(clip_stream, clip_game)
                    #print(set_flair)
                    if set_flair is not None:
                        self.submission.flair.select(set_flair)
            except:
                pass

print('Auto moderating..')
while True:
    for submission in reddit.subreddit(MASTER).new():
        skip = auto_moderate(submission).low_engagement()
        if skip:
            continue
        auto_moderate(submission).handle_twitch_clip()
