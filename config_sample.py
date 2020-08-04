MASTER = 
REDDIT_USER = 
REDDIT_PASS = 
REDDIT_CLIENT_ID = 
REDDIT_CLIENT_SECRET = 
STREAMABLE_USER = 
STREAMABLE_PASS = 
TWITCH_SECRET = 

## Auto moderation
DETERMINE_BAD = [1, 1] # score, num_comments
DELETE_BAD_AFTER = 3 # in hours
SKIP_BAD_DELETE_AFTER = 24 # in hours
DELETE_OLD_CLIP = 30 # in days

## Auto reposting domain clips.twitch.tv
ALLOWED_SUBS = []
MIN_SCORE = 100


## Auto reposting
TARGETS =
ALLOWED_DOMAINS = ['clips.twitch.tv', 'twitter.com']
POST_FREQUENCY = 60 # in minutes, cut in half if not first sub of TARGETS
ALLOW_BANNED_AUTHORS = False
BANNED_FLAIRS = []
BANNED_TITLES = []
SCORE_MAIN = 10 # first sub of TARGETS, # of upvotes req.
SCORE_OTHER = 5 # other subs, # of upvotes req.

## Auto mirror/vod

