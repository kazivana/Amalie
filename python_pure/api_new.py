import math

from dotenv import load_dotenv
from datetime import datetime, date, timedelta
import time
import os
import pandas as pd
import psycopg2
import requests
import json

# Load variables from .env file directly so we wouldn't have to hard code parameters
load_dotenv()

# List of APIs to extract data from
api = ['https://p0c1rtf2ce.execute-api.eu-central-1.amazonaws.com/prod/e06990a6-2c04-4bb3-a5be-48ffea49f603',
       'https://p0c1rtf2ce.execute-api.eu-central-1.amazonaws.com/prod/22626fb7-dbbb-45ef-8787-f3bccbb2526b',
       'https://p0c1rtf2ce.execute-api.eu-central-1.amazonaws.com/prod/f07231f8-39bc-4133-b799-591665b166a9',
       'https://p0c1rtf2ce.execute-api.eu-central-1.amazonaws.com/prod/230ac88f-4186-482c-ac02-f3b93e618b03',
       'https://p0c1rtf2ce.execute-api.eu-central-1.amazonaws.com/prod/0919e6f9-d6cf-4b2c-9321-01b6f54054e3',
       # 'https://p0c1rtf2ce.execute-api.eu-central-1.amazonaws.com/prod/efba0291-d89f-4966-908a-97fb1afe7f26',
       'https://p0c1rtf2ce.execute-api.eu-central-1.amazonaws.com/prod/88ff105f-2dde-4541-a3d7-0d6143b5452c']

params = {
    'host': os.getenv('host'),
    'database': os.getenv('database'),
    'user': os.getenv('user'),
    'password': os.getenv('password'),
    'port': os.getenv('port')
}


# Object with data from APIs which is received on regular time intervals
class CleverfarmAPI:

    # Initialize API and create a new dictionary called data
    def __init__(self):
        self.api = api
        self.data = {}

    # Taking from the API the names of the variables for creating tables directly
    def get_features(self):
        for req in self.api:
            res = requests.get(req)
            if res.status_code == 200:
                for sensor in res.json()['sensors']:
                    if sensor['feature'] not in self.data.keys():
                        self.data.update({sensor['feature']: pd.DataFrame()})
            else:
                print('CONNECTION ERROR: ', req.status_code)
        return self.data
        
    # Creating a dataframe from the API
    def create_df_from_api(self):
        for req in self.api:
            res = requests.get(req)
            if res.status_code == 200:
                for sensor in res.json()['sensors']:
                        df = pd.DataFrame(sensor['data'])
                        # Adding a column with sensor's name
                        df.insert(0, 'sensor_name', res.json()['name'])
                        # Separating date to date column
                        df.insert(1, 'date', df['time'].str.slice(start=0, stop=10))
                        # Assigning time column to store only time
                        df['time'] = df['time'].str.slice(start=11, stop=19)
                        # Last column with signal property
                        df.insert(4, 'signal', res.json()['signal'])
                        temp = [self.data[sensor['feature']], df]
                        self.data[sensor['feature']] = pd.concat(temp)
            else:
                print('CONNECTION ERROR: ', req.status_code)
        return self.data

# The data has now been retrieved from the API, so we work on the Database data next

# Object for data stored in DB
class DataDB:
    def __init__(self, schema):
        self.params = params # the parameters are the connection to the database, used to initialize DB
        self.conn = psycopg2.connect(**params) # creating the connection to the DB
        self.schema = schema # the data will be distributed by schemas, each sensor will have its own schema

    # Select any NA data
    def get_nan(self, tables):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT sensor_name,date,time FROM %s.\"%s\" WHERE value = double precision 'NaN'" % (self.schema, tables))
            temp = cursor.fetchall()
            cursor.close()
            return temp

    # function for retrieving data for current day and previous day
    def get_actual(self, tables):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT sensor_name,date,time FROM %s.\"%s\" WHERE date >= '%s'" % (self.schema, tables, (date.today() - timedelta(days=1))))
            temp = cursor.fetchall()
            cursor.close()
            return temp

    # Create rows for the data table
    def insert_rows(self,tables, rows):
        if self.conn:
            query = "INSERT INTO %s.\"%s\"(sensor_name,date,time,value,signal) VALUES(%%s,%%s,%%s,%%s,%%s)" % (self.schema, tables)
            cursor = self.conn.cursor()
            cursor.execute(query,rows)
            self.conn.commit()
            cursor.close()

    # Check whether there is a new NA value
    def update_nan(self,tables,row):
        if self.conn:
            query = "UPDATE %s.\"%s\" SET signal = %%s, value = %%s " \
                    "WHERE time = %%s AND date = %%s AND sensor_name = %%s AND value = double precision 'NaN'" % (self.schema, tables)
            cursor = self.conn.cursor()
            cursor.execute(query,row)
            self.conn.commit()
            cursor.close()
            print('Updated data in {} successfully'.format(tables))

    # Calculating the statistical values
    def collect_stats(self,tables,month_start, month_end):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT sensor_name,value FROM %s.\"%s\" WHERE date >= '%s' AND date <= '%s' " % (
            self.schema, tables, month_start, month_end))
            data_for_stats = cursor.fetchall()
            cursor.close()
        temp = pd.DataFrame(data_for_stats, columns=['sensor_name','value'])
        df = pd.DataFrame()
        df.insert(0,'sensor_name',temp['sensor_name'].unique())
        df.insert(1,'year',month_start.year)
        df.insert(2, 'month', month_start.month)
        df.insert(3, 'feature', tables)
        df.insert(4, 'mean', temp.groupby(['sensor_name']).mean().values)
        df.insert(5, 'min', temp.groupby(['sensor_name']).min().values)
        df.insert(6, 'max', temp.groupby(['sensor_name']).max().values)
        return df

    # Inserting the calculations from previous function into the tables
    def insert_stats(self,tables,feat_stats):
        stat_rows = [tuple(x) for x in feat_stats.to_numpy()]
        if self.conn:
            query = "INSERT INTO %s.cleverfarm_stats(sensor_name,year,month,feature,mean,min,max) " \
                    "VALUES(%%s,%%s,%%s,%%s,%%s,%%s,%%s)" % (self.schema)
            cursor = self.conn.cursor()
            cursor.executemany(query, stat_rows)
            self.conn.commit()
            cursor.close()
            print('Inserted stats for {} successfully'.format(tables))

# Script run
# Start timer
start = time.time()
# Init empty object with api list
new_set = CleverfarmAPI()
# Get all features names and update them as dictionary key
new_set.get_features()
# Get data from all api and store it in a dict variable {'feature_name':[data]}
data = new_set.create_df_from_api()
# Init database object for specified schema
server = DataDB('cleverfarm')

for table in data.keys():
    # For each feature create list of tuples (rows) from dataset
    rows = [tuple(x) for x in data.get(table).to_numpy()]
    # Collect data for today from database
    actual = server.get_actual(table)
    nan = server.get_nan(table)
    for row in rows:
        if (row[0],datetime.strptime(row[1], "%Y-%m-%d").date(),datetime.strptime(row[2],"%H:%M:%S").time()) not in actual:
            server.insert_rows(table,row)
            print('Added data to {} successfully'.format(table))
        if ((row[0],datetime.strptime(row[1], "%Y-%m-%d").date(),datetime.strptime(row[2],"%H:%M:%S").time()) in nan) \
                    & (not math.isnan(row[3])):
            server.update_nan(table, row[::-1])

    # Collect monthly stats for a previous month on the first day of next month
    if date.today().day == 1:
        month_end = (date.today() - timedelta(days=1))
        month_start = month_end.replace(day=1)
        feature_stats = server.collect_stats(table,month_start,month_end)
        server.insert_stats(table, feature_stats)

# Stop timer. Output time of run
print(time.time()-start)
