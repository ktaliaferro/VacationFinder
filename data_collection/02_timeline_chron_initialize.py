"""This initializes the chron_progress table in my MySQL database
to zero so that I can then use timeline_chron.py to begin pulling Twitter
users' Timelines from Twitter every 15 minutes.  Each time that
timeline_chron.py runs, it will update the chron_progress table in MySQL."""

from twython import Twython
import pandas as pd
import re
import matplotlib as plt
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import datetime

from mysql_login_info import sql_username, sql_password
from twitter_keys import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET

# connect to my local mySQL server and open the vacation database
engine = create_engine('mysql+mysqldb://'+sql_username+':'+sql_password+'@127.0.0.1:3306/vacation', echo=False)

# initialize progress to zero
df_progress = pd.DataFrame({'Progress':[0]})

# copy the progress to the database
df_progress.to_sql('chron_progress', engine, if_exists='replace', index=False)
