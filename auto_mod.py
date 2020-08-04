#! python 3
import praw
import requests
import json
import time
from datetime import datetime, timedelta
import pytz
import dateutil.parser
import config

reddit = praw.Reddit(
    user_agent='u/' + config.REDDIT_USER + 'v1.0',
    username=config.REDDIT_USER,
    password=config.REDDIT_PASS,
    client_id=config.REDDIT_CLIENT_ID,
    client_secret=config.REDDIT_CLIENT_SECRET
)


class auto_moderate:
    def __init__(self, submission=None):
        self.subreddit = config.MASTER
        self.submission = submission
        ## special exception because no api support
        self.twitch_api_url = 'https://api.twitch.tv/kraken'
        self.headers = {
            'Client-ID' : config.TWITCH_SECRET,
            'Accept': 'application/vnd.twitchtv.v5+json'
        }
    ## Request data from twitch
    def generate_twitch_data(self, endpoint, url):
        requested_url = self.twitch_api_url + '/' + endpoint + '/' + url
        r = requests.get(url=requested_url, headers=self.headers)
        if r.status_code == 200:
            try:
                twitch_data = json.loads(r.text)
                return twitch_data
            except:
                return None
        return None
    def generate_mirror_link(self, video_url):
        STREAM_API = 'https://api.streamable.com/import?url='
        api_query_url = (STREAM_API+video_url).strip()
        r = requests.get(api_query_url, auth=(config.STREAMABLE_USER, config.STREAMABLE_PASS))
        if r.status_code == 200:
            shortcode = r.json()['shortcode']
            return 'https://streamable.com/'+shortcode
        return None
    def twitch_timestamp(self, timestamp):
        ts = dateutil.parser.parse(timestamp)
        ts = ts.astimezone(pytz.timezone('UTC'))
        ts = ts.replace(tzinfo = None)
        return ts
    def attach_message(self, msg, sub=None, sticky=None, remove=None , reason=None):
        if sub is None:
            sub = self.submission
        comment = sub.reply(msg + '\n\n___\n\nPlease contact the moderators of this subreddit if you have any questions or concerns.')
        if sticky:
            comment.mod.distinguish(sticky=True)
        if remove:
            sub.mod.remove()
        if reason:
            print(sub.title, 'removed: ', reason)
    ## Removes boring posts
    def low_engagement(self):
        for submission in reddit.subreddit(self.subreddit).new():
            try:
                min_age = datetime.utcnow() - timedelta(hours=config.DELETE_BAD_AFTER)
                max_age = datetime.utcnow() - timedelta(hours=config.SKIP_BAD_DELETE_AFTER)
                post_age = datetime.utcfromtimestamp(submission.created_utc)
                if submission.score <= config.DETERMINE_BAD[0] and submission.num_comments <= config.DETERMINE_BAD[1] and post_age <= min_age and not post_age <= max_age:
                    self.attach_message('This post has automatically been deleted because of low engagement.', sub=submission, sticky=True, remove='low engagement')
            except:
                pass
    def sort_flair(self, name, game):
        for template in reddit.subreddit(self.subreddit).flair.link_templates:
            try:
                flair_text = template['text']
                if name in flair_text or flair_text in game:
                    return template['id']
                if game in flair_text or flair_text in game:
                    return template['id']
            except:
                return None
        return None
    ## Sets flair, checks self promo, deletes old
    def handle_twitch_clip(self):
        self.low_engagement()
        if self.submission.domain == 'clips.twitch.tv' and 'clips.twitch.tv' in self.submission.url:
            try:
                trim_url = self.submission.url.split('clips.twitch.tv/')[1]
                clip_data = self.generate_twitch_data('clips', trim_url)
                clip_stream = clip_data['broadcaster']['display_name']
                clip_by = clip_data['curator']['display_name']
                clip_game = clip_data['game']
                clip_created = clip_data['created_at']
                vod_link = clip_data['vod']['url']
                ## Check if self promotion
                if clip_stream and clip_by and clip_stream == clip_by:
                    self.attach_message('This post has automatically been deleted because of self promotion.', sticky=True, remove=True, reason='self promotion')
                    return
                ## Check if old clip
                twitch_ts = self.twitch_timestamp(clip_created) + timedelta(days=config.DELETE_OLD_CLIP)
                today = datetime.utcnow()
                if clip_stream and today > twitch_ts:
                    self.attach_message('This post has automatically been deleted because the clip is more than', config.DELETE_OLD_CLIP ,'days old.', sticky=True, remove=True, reason='old clip')
                    return
                ## Check if no flair
                sub_flair = self.submission.link_flair_text
                if clip_stream and clip_game and sub_flair is None:
                    set_flair = self.sort_flair(clip_stream, clip_game)
                    if set_flair is not None:
                        self.submission.flair.select(set_flair)
                mirror_link = self.generate_mirror_link(self.submission.url)
                if mirror_link and vod_link:
                    message = f'###[Mirror Link]({mirror_link})\n###[VOD Link]({vod_link})'
                elif mirror_link and not vod_link:
                    message = f'###[Mirror Link]({mirror_link})'
                elif vod_link and not mirror_link:
                    message = f'###[VOD Link]({vod_link})'
                if message:
                    self.attach_message(message, sticky=True)
            except:
                pass


def initiate(sub):
    start_time = time.time()
    print('Streaming new submissions ...')
    for submission in reddit.subreddit(sub).stream.submissions():
        #auto_moderate().low_engagement()
        if submission.created_utc < start_time:
            continue  # Ignore old messages
        auto_moderate(submission).handle_twitch_clip()



if __name__ == '__main__':
    initiate(config.MASTER)