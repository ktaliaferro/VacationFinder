"""Run this file every 15 minutes until all timeline data is pulled
from Twitter.  The process will take about about 12 hours."""

from twython import Twython
import pandas as pd
import re
import matplotlib as plt
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import datetime

from mysql_login_info import sql_username, sql_password
from twitter_keys import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET

# Print log file entry
print ''
print datetime.datetime.today().__str__()

# Twitter authentication
twitter = Twython(APP_KEY, APP_SECRET,
                  OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

# connect to my local mySQL server and open the vacation database
engine = create_engine('mysql+mysqldb://'+sql_username+':'+sql_password+'@127.0.0.1:3306/vacation', echo=False)

# Pull the vacation tweet data out of the mySQL server
# and put in in the original dataframe.
sql_query = 'SELECT * FROM vacation_tweets_w_name'
df_both = pd.read_sql_query(sql_query,engine).sort('Tweet ID')
print len(df_both.index), 'total user timelines to process'
df_both.head(2)

# Get the chron progress from the dataframe
sql_query = 'SELECT * FROM chron_progress'
df_progress = pd.read_sql_query(sql_query,engine)
progress = df_progress['Progress'][0]

# Filter out the vacation tweet data that has already been processed
df_both = df_both[df_both['Tweet ID']>progress].sort('Tweet ID')
print len(df_both.index), 'user timelines left to process'
df_both.head(2)


# Get the first 85 users' timelines
# count=200 is the maximum allowed amount
# 180 of such requests are allowed per 15 minutes
timelines = []
length = len(df_both['Screen Name'].values)
users_skipped = 0
user_timelines_to_query = 85
queries_per_timeline = 2
for i in range(user_timelines_to_query):
    if i >= length:
        break
    screen_name = df_both.iloc[i]['Screen Name']
    try:
        next_timeline = twitter.get_user_timeline(screen_name=screen_name, count=200)
    except Exception as e:
        print 'exception at query', i
        print e
        #break
        print 'skipping user', screen_name
        users_skipped += 1
        continue
    current_user_timeline=[next_timeline]
    for j in range(1, queries_per_timeline):
        if len(current_user_timeline[-1])<200:
            break
        max_id=min([status['id'] for status in current_user_timeline[-1]])-1
        try:
            next_timeline = twitter.get_user_timeline(screen_name=screen_name, count=200, max_id=max_id)
        except:
            break
        current_user_timeline.append(next_timeline)  
    timelines.append(current_user_timeline)
    progress = df_both.iloc[i]['Tweet ID']

    
print i+1-users_skipped, 'user timelines processed'
print users_skipped, 'user timelines skipped'
print len(df_both.index) - i - 1, 'user timelines left to process'

# Put the timeline tweets in a dataframe
time_timeline = []
time_texts = []
time_ids = []
time_times = []
time_destinations = []
time_names = []
time_screen_names = []
for i in range(len(timelines)):
    screen_name = df_both.iloc[i]['Screen Name']
    destination = df_both.iloc[i]['Destination']
    for user_timeline in timelines[i]:
        for tweet in user_timeline:
            time_timeline.append(screen_name)
            time_texts.append(tweet['text'])
            time_ids.append(tweet['id'])
            time_times.append(tweet['created_at'])
            time_destinations.append(destination)
            time_names.append(tweet['user']['name'])
            time_screen_names.append(tweet['user']['screen_name'])
    df_timeline = pd.DataFrame({'Timeline': time_timeline,
                                'Tweet': time_texts,
                                'Tweet ID': time_ids,
                                'Time': time_times,
                                'Destination': time_destinations,
                                'Full Name': time_names,
                                'Screen Name': time_screen_names
                               })


# Change the character encoding to utf-8.
# MySQL will complain otherwise.
for col in df_timeline.columns.values:
    if df_timeline[col].dtype=='object':
        df_timeline[col]=df_timeline[col].str.encode('utf-8', errors='ignore')

# Save the timelines to my mySQL server
df_timeline.to_sql('timeline_tweets', engine, if_exists='append', index=False)

# put the progress in a dataframe
df_progress = pd.DataFrame({'Progress':[progress]})

# copy the progress dataframe to the MySQL database
df_progress.to_sql('chron_progress', engine, if_exists='replace', index=False)

# Print the number of tweets processed
print len(df_timeline.index), 'tweets processed'

# Print the time remaining, assuming
# 85 timelines collected 3 times every hour
print '{0:.1f} hours remain'.format(len(df_both.index) * 1.0 / 85 / 3)
