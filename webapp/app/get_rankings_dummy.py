"""This dummy version of get_rankings imports pre-computed rankings
from the MySQL server and is used for testing purposes."""

# packages
import re
import time
import pandas as pd
import pymysql as mdb
from sqlalchemy import create_engine

# files in this directory
from mysql_login_info import sql_username, sql_password
import preprocessing

def get_rankings_dummy():
    # Connect to my local mySQL server and open the vacation database
    engine = create_engine('mysql+mysqldb://'+sql_username+':'+sql_password+'@127.0.0.1:3306/vacation', echo=False)
    
    # Pull the pre-computed rankings out of MySQL
    sql_query = 'SELECT * FROM interest_destination_dummy'
    df_interest_destination = pd.read_sql_query(sql_query,engine)

    # Put the pre-computed rankings in table format
    interest_col = df_interest_destination['Interest'].values.tolist()
    destination_col = df_interest_destination['Destination'].values.tolist()
    interest_destination = []
    length = len(interest_col)
    for i in range(length):
        interest_destination.append([destination_col[i],interest_col[i]])
    return interest_destination
