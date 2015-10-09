"""This will stem all of the tweets in the timeline_tweets table and
put them in the timeline_tweets_stemmed table."""

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import time
import preprocessing
from mysql_login_info import sql_username, sql_password
import datetime

start_time = time.clock()

# connect to my local mySQL server and open the vacation database
engine = create_engine('mysql+mysqldb://'+sql_username+':'+sql_password+'@127.0.0.1:3306/vacation', echo=False)


chunk_size = 10000
i = 0
while True:
    # Pull the timeline data out of the mySQL server
    # and put it in a pandas dataframe.
    sql_query = 'SELECT * FROM timeline_tweets ORDER BY `Tweet ID` LIMIT ' + str(chunk_size) + ' OFFSET ' + str(i*chunk_size)
    df_timeline = pd.read_sql_query(sql_query,engine)

    if len(df_timeline.index)<1:
        break
    # Stem the Tweet column
    def stem(s):
        return preprocessing.preprocess_pipeline(s, return_as_str=True, do_remove_stopwords=True, do_clean_html=False)
    df_timeline['Tweet']=df_timeline['Tweet'].str.decode('utf-8').str.encode('ascii', errors='ignore').apply(stem)

    # Save the data on my mySQL server
    df_timeline.to_sql('timeline_tweets_stemmed', engine, if_exists='append', index=False)
    i += 1
    print datetime.datetime.today().__str__()
    print 'chunk size:', chunk_size
    print 'chunks processed:', i

end_time = time.clock()

print 'runtime:', (end_time - start_time) / 60, 'minutes'
