"""This function takes users interests as inputs and outputs a list of
ranked vacation destinations with top interests for each destination.
To rank destinations, the app uses data that I've collected from Twitter
and stored in MySQL.  user_interests is a assumed to be a string
consiting of interests separated by commas.  The output is a 2D list of
strings.  The left column has destinations and the right column has
the top three interests for that destination."""

# packages
import re
import time
import pandas as pd
import pymysql as mdb
from sqlalchemy import create_engine

# files in this directory
from mysql_login_info import sql_username, sql_password
import preprocessing

def get_rankings(user_interests):
    destinations=[]
    df_destinations=pd.read_csv('vacation_destinations.txt', header=None, names=['Destination'])
    destinations = sorted(df_destinations['Destination'].values.tolist())

    # connect to my local mySQL server and open the vacation database
    engine = create_engine('mysql+mysqldb://'+sql_username+':'+sql_password+'@127.0.0.1:3306/vacation', echo=False)

    # Parse user input, stem it, and make regexes
    user_input = user_interests
    def stem(s):
            return preprocessing.preprocess_pipeline(s, return_as_str=True, do_remove_stopwords=True, do_clean_html=False)
    interests_regex={}
    max_interests = 10
    for interest in user_input.split(',')[:max_interests]:
        if interest == '':
            continue
        # remove any characters that that aren't alphanumeric.
        interest = re.sub(r'[^\w]+', '', interest)
        if False:
            # Insert MySQL regex for spaces (this isn't working yet).  Once I
            # get this working, make sure to fix the re.sub line above
            # so that it doesn't remove spaces.
            interests_regex[interest.strip()]= re.sub(' ',r'[[:space:]]',stem(interest))
        interests_regex[interest.strip()]= stem(interest)
    interests=interests_regex.keys()
    print len(interests), 'interests'
    print interests_regex

    # Put the destinations in a dataframe to use in the next step
    df_destinations = pd.DataFrame({'Destination':destinations}).set_index('Destination')
    df_destinations.head()
       
    # Count the number of tweets for each destination for each interest
    destinations_interests = df_destinations.copy()
    db = mdb.connect(user=sql_username, host="localhost", passwd=sql_password, db="vacation", charset='utf8')
    interests_processed = 0
    for interest in interests:
        sql_query = ("SELECT Destination, COUNT(*) AS " + interest +
                     " FROM timeline_tweets_stemmed_unique WHERE Tweet REGEXP '[[:<:]]" +
                     interests_regex[interest] + "[[:>:]]' GROUP BY Destination")
        with db:
            cur = db.cursor()
            cur.execute(sql_query)
            query_results = cur.fetchall()
        query_results = map(list, zip(*[list(i) for i in query_results]))
        if len(query_results) == 0:
            interests_processed += 1
            print interests_processed, 'interests processed'
            continue
        df_timeline = pd.DataFrame({'Destination': query_results[0], interest: query_results[1]}).set_index('Destination')
        destinations_interests = destinations_interests.join(df_timeline, how='outer').fillna(0)
        interests_processed += 1
        print interests_processed, 'interests processed'

    # Rank the interests for each destination.  Normalize the number of tweets.
    def normalize(x):
            if x.std() > 0.01:
                return (x-x.mean())/x.std()
            else:
                return x-x.mean()
    destinations_interests_scores = destinations_interests.copy()
    destinations_interests_scores = destinations_interests_scores.apply(normalize)

    # Store the top three interests for each destination in a dataframe
    destination_col = destinations_interests_scores.sum(axis=1).sort(ascending=False, inplace=False).index.values.tolist()
    interest_col = []
    for destination in destination_col:
        interest_col.append(', '.join(destinations_interests_scores.loc[destination].sort(ascending=False, inplace=False).index.values.tolist()[:3]))
    df_interest_destination = pd.DataFrame({'Interest': interest_col, 'Destination': destination_col})
    df_interest_destination = df_interest_destination[['Destination', 'Interest']]
    df_interest_destination.head()
    
    # Put the top interest for each destination in table format
    interest_col = df_interest_destination['Interest'].values.tolist()
    destination_col = df_interest_destination['Destination'].values.tolist()
    interest_destination = []
    length = len(interest_col)
    for i in range(length):
        interest_destination.append([destination_col[i],interest_col[i]])

    # Return the results as a 2D list
    return interest_destination

