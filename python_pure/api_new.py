from dotenv import load_dotenv
from datetime import datetime
import time
import os
import pandas as pd
import psycopg2
import requests
import json

# Load variables from .env file
load_dotenv()
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


# Object with data from APIs
class CleverfarmAPI:
    def __init__(self):
        self.api = api
        self.data = {}

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

# Object for data stored in DB
class DataDB:
    def __init__(self, schema):
        self.params = params
        self.conn = psycopg2.connect(**params)
        self.schema = schema

    def get_nan(self, tables):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT sensor_name,date,time FROM %s.%s WHERE value = double precision 'NaN'" % (self.schema, tables))
            temp = cursor.fetchall()
            cursor.close()
            return temp

    def get_actual(self, tables):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT sensor_name,date,time FROM %s.%s WHERE date = '%s' " % (self.schema, tables, datetime.now().date()))
            temp = cursor.fetchall()
            cursor.close()
            return temp

    def insert_rows(self,tables, rows):
        if self.conn:
            query = "INSERT INTO %s.%s(sensor_name,date,time,value) VALUES(%%s,%%s,%%s,%%s)" % (self.schema, tables)
            cursor = self.conn.cursor()
            cursor.executemany(query,rows)
            self.conn.commit()
            cursor.close()
            print('Added data to {} successfully'.format(tables))

    def update_nan(self,tables,rows):
        if self.conn:
            query = "INSERT INTO %s.%s(sensor_name,date,time,value) VALUES(%%s,%%s,%%s,%%s)" % (self.schema, tables)
            cursor = self.conn.cursor()
            cursor.executemany(query,rows)
            self.conn.commit()
            cursor.close()
            print('Updated data in {} successfully'.format(tables))



start = time.time()

# Init empty object with api list
new_set = CleverfarmAPI()
# Get all features names and update them as dictionary key
ft = list(new_set.get_features().keys())
print(ft)

# Get data from all api and store it in a dict variable {'feature_name':[data]}
data = new_set.create_df_from_api()
# Init database object for specified schema
server = DataDB('cleverfarm')

'''for table in data.keys():
    # For each feature create list of tuples (rows) from dataset
    rows = [tuple(x) for x in data.get(table).to_numpy()]
    # Collect data for today from database
    actual = server.get_actual(table)
    # If there is any data, check for NaN values updates
    if actual:
        nan = server.get_nan(table)
        for row in rows:
            if row in nan:
                print('NEW')
    # If no data for today, insert all data received from api
    else:
        server.insert_rows(table, rows)
'''




print(time.time()-start)