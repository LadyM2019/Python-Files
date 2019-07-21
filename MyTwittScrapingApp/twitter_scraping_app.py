

import tweepy
import csv
import json


# load Twitter API credentials

with open('twitter_credentials.json') as cred_data:
    info = json.load(cred_data)
    consumer_key = info['CONSUMER_KEY']
    consumer_secret = info['CONSUMER_SECRET']
    access_key = info['ACCESS_KEY']
    access_secret = info['ACCESS_SECRET']


def get_100_tweets(twitter_handle):

    # create authentication for accessing Twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    # initialize Tweepy API
    api = tweepy.API(auth)

    # open the spreadsheet we will write to
    with open(f'{twitter_handle}.csv', 'w') as file:

        w = csv.writer(file)

        # write header row to spreadsheet
        w.writerow(['timestamp', 'tweet_text', 'username', 'followers_count', 'profile_image'])

        # for each tweet matching our twitter handle, write row info to the spreadsheet
        for tweet in tweepy.Cursor(api.search, q=twitter_handle+' -filter:retweets', \
                                   lang="en", tweet_mode='extended').items(100):
            w.writerow([tweet.created_at, tweet.full_text.replace('\n', ' ').encode('utf-8'),
                        tweet.user.screen_name.encode('utf-8'),
                        tweet.user.followers_count, tweet.user.profile_image_url])
    

if __name__ == '__main__':

    # Enter the twitter handle of the person concerned

    get_100_tweets(input("Enter the twitter handle of the person whose tweets you want to download:- "))
