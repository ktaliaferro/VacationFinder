"""This will create a timeline_tweets_stemmed_unique table that contains
all unique tweets from timeline_tweets_stemmed."""

import pandas as pd
import re
import matplotlib as plt
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

import numpy as np
import time

from mysql_login_info import sql_username, sql_password
import preprocessing

# connect to my local mySQL server and open the vacation database
engine = create_engine('mysql+mysqldb://'+sql_username+':'+sql_password+'@127.0.0.1:3306/vacation', echo=False)

# Pull the timeline data out of the mySQL server
# and put in in the original dataframe.

sql_query = 'SELECT * FROM timeline_tweets_stemmed GROUP BY `Tweet ID`, Destination'
df_timeline = pd.read_sql_query(sql_query,engine)
print len(df_timeline.index), 'rows'
df_timeline.head(2)

# Save the data on my mySQL server

if False:
    chunk_size = 10000
    chunk = 0
    while True:
        df_chunk = df_timeline.iloc[chunk*chunk_size:(chunk + 1)*chunk_size]
        if len(df_chunk.index) < 1:
            break
        df_chunk.to_sql('timeline_tweets_stemmed_unique', engine, if_exists='append', index=False)
        chunk += 1
        print chunk, 'chunks completed'
    print 'task completed'
