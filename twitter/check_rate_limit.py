import os, twitter, time

# load Twitter app credentials from environment variables
api_key = os.environ['TWITTER_API']
api_secret = os.environ['TWITTER_SECRET']
access_token = os.environ['TWITTER_ACCESS_TOKEN']
access_secret = os.environ['TWITTER_ACCESS_SECRET']

# instantiate Twitter API object
api = twitter.Api(
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token_key=access_token,
    access_token_secret=access_secret,
    sleep_on_rate_limit=True
)

api.InitializeRateLimit()
time.sleep(5)
limit_status = api.rate_limit.get_limit('https://api.twitter.com/1.1/followers/list.json')
print(limit_status)
print('resets in:', (limit_status.reset - time.time()) / 60, 'minutes')
