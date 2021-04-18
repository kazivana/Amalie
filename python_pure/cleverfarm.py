import requests
import json
import pandas as pd
import psycopg2
from datetime import datetime
import math
import time

def main(api, params):
    # Initializing data frame for each value type
    swp = pd.DataFrame()
    tmp = pd.DataFrame()
    prs = pd.DataFrame()
    hum = pd.DataFrame()
    rnf = pd.DataFrame()
    lfw = pd.DataFrame()
    wnd = pd.DataFrame()
    wng = pd.DataFrame()
    wns = pd.DataFrame()
    for req in api:
        resp = requests.get(req) # Get request
        if resp.status_code == 200:
            for sensor in resp.json()['sensors']: # Pattern is the same, explained on SWP feature
                if sensor['feature'] == "SWP":
                    df = pd.DataFrame(sensor['data'])  # Create a data frame from sensor's data
                    df.insert(0, 'sensor_name', resp.json()['name'])  # Adding a column with sensor's name
                    df.insert(1, 'date', df['time'].str.slice(start=0, stop=10))  # Separating date to date column
                    df['time'] = df['time'].str.slice(start=11, stop=19)  # Assigning time column to store only time
                    swp = swp.append(df)  # Store result in main value's table
                elif sensor['feature'] == "TEMPERATURE":
                    df = pd.DataFrame(sensor['data'])
                    df.insert(0, 'sensor_name', resp.json()['name'])
                    df.insert(1, 'date', df['time'].str.slice(start=0, stop=10))
                    df['time'] = df['time'].str.slice(start=11, stop=19)
                    tmp = tmp.append(df)
                elif sensor['feature'] == "PRESSURE":
                    df = pd.DataFrame(sensor['data'])
                    df.insert(0, 'sensor_name', resp.json()['name'])
                    df.insert(1, 'date', df['time'].str.slice(start=0, stop=10))
                    df['time'] = df['time'].str.slice(start=11, stop=19)
                    prs = prs.append(df)
                elif sensor['feature'] == "HUMIDITY":
                    df = pd.DataFrame(sensor['data'])
                    df.insert(0, 'sensor_name', resp.json()['name'])
                    df.insert(1, 'date', df['time'].str.slice(start=0, stop=10))
                    df['time'] = df['time'].str.slice(start=11, stop=19)
                    hum = hum.append(df)
                elif (sensor['feature'] == "RAINFALL") & (sensor['aggregation'] == "SUM"):
                    df = pd.DataFrame(sensor['data'])
                    df.insert(0, 'sensor_name', resp.json()['name'])
                    df.insert(1, 'date', df['time'].str.slice(start=0, stop=10))
                    df['time'] = df['time'].str.slice(start=11, stop=19)
                    rnf = rnf.append(df)
                elif sensor['feature'] == "LEAF_WETNESS":
                    df = pd.DataFrame(sensor['data'])
                    df.insert(0, 'sensor_name', resp.json()['name'])
                    df.insert(1, 'date', df['time'].str.slice(start=0, stop=10))
                    df['time'] = df['time'].str.slice(start=11, stop=19)
                    lfw = lfw.append(df)
                elif sensor['feature'] == "WIND_DIRECTION":
                    df = pd.DataFrame(sensor['data'])
                    df.insert(0, 'sensor_name', resp.json()['name'])
                    df.insert(1, 'date', df['time'].str.slice(start=0, stop=10))
                    df['time'] = df['time'].str.slice(start=11, stop=19)
                    wnd = wnd.append(df)
                elif sensor['feature'] == "WIND_GUST":
                    df = pd.DataFrame(sensor['data'])
                    df.insert(0, 'sensor_name', resp.json()['name'])
                    df.insert(1, 'date', df['time'].str.slice(start=0, stop=10))
                    df['time'] = df['time'].str.slice(start=11, stop=19)
                    wng = wng.append(df)
                elif sensor['feature'] == "WIND_SPEED":
                    df = pd.DataFrame(sensor['data'])
                    df.insert(0, 'sensor_name', resp.json()['name'])
                    df.insert(1, 'date', df['time'].str.slice(start=0, stop=10))
                    df['time'] = df['time'].str.slice(start=11, stop=19)
                    wns = wns.append(df)
                else:
                    continue;
        else:
            print("CONNECTION ERROR: ",req.status_code)
    dt_names = {  # A dictionary with dt names corresponding to dt
        'swp': swp,
        'tmp': tmp,
        'prs': prs,
        'hum': hum,
        'rnf': rnf,
        'lfw': lfw,
        'wnd': wnd,
        'wng': wng,
        'wns': wns
    }
    for dt in dt_names:  # NOW THIS LOOP IS SAFE! Prevents duplication, inserts new values, if old is NaN
        # Create list of tuples from dt
        tuples = [tuple(x) for x in dt_names[dt].to_numpy()]
        # Get existing dt from server
        server_date = get_date(params,dt)
        server_na = get_na(params,dt)
        # If first init, simply inserts everything
        if len(server_date) < 1:
            query = "INSERT INTO cleverfarm.%s(sensor_name,date,time,value) VALUES(%%s,%%s,%%s,%%s)" % dt
            execute_many_query(params, query,tuples)
        else:
            result_dates = []
            result_nan = []
            for row in tuples:
                # If date+time doesn't exists in server dt, inserts a new row
                if (row[0],datetime.strptime(row[1], "%Y-%m-%d").date(),
                    datetime.strptime(row[2], "%H:%M:%S").time()) not in server_date:
                    result_dates.append(row)
                elif ((row[0],datetime.strptime(row[1], "%Y-%m-%d").date(),
                              datetime.strptime(row[2],"%H:%M:%S").time()) in server_na) &\
                        (not math.isnan(row[3])):
                    result_nan.append(row[::-1])
            if len(result_dates) > 0:
                query = "INSERT INTO cleverfarm.%s(sensor_name,date,time,value) VALUES(%%s,%%s,%%s,%%s)" % dt
                execute_many_query(params, query, result_dates)
            if len(result_nan) > 0:
                query = "UPDATE cleverfarm.%s SET value = %%s WHERE time = %%s AND date = %%s AND sensor_name = %%s AND " \
                        "value = " \
                        "double precision 'NaN'" % dt
                execute_many_query(params,query,result_nan)


def execute_many_query(params,query,tuples):
    conn = psycopg2.connect(**params)
    if conn:
        cursor = conn.cursor()
        cursor.executemany(query,tuples)
        conn.commit()
        print("QUERY EXECUTION IS DONE")
        cursor.close()


def get_date(params,dt):
    conn = psycopg2.connect(**params)
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT sensor_name,date,time FROM cleverfarm.%s " % dt)
        temp = cursor.fetchall()
        cursor.close()
        return temp


def get_na(params,dt):
    conn = psycopg2.connect(**params)
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT sensor_name,date,time FROM cleverfarm.%s WHERE value = double precision 'NaN'" % dt)
        temp = cursor.fetchall()
        cursor.close()
        return temp


# Function for exploring json files in python. Not needed in the end program, can be removed
def print_json(obj):
    str = json.dumps(obj, sort_keys=True, indent=3)
    print(str)


# WARNING! Run this func only once, to avoid further issues!!!
# Init function to create all necessary tables and grant permissions on them
def create_tables(params):
    names = ['swp','tmp','prs','hum','rnf','lfw','wnd','wng','wns']
    for name in names:
        query = "CREATE TABLE cleverfarm.%s(id SERIAL PRIMARY KEY ,sensor_name VARCHAR NOT NULL,date DATE NOT NULL," \
                "time TIME NOT NULL,value FLOAT);" \
                "GRANT ALL ON SEQUENCE cleverfarm.%s_id_seq TO postgres;" \
                "GRANT ALL ON TABLE cleverfarm.%s TO postgres;" % (name,name,name)
        conn = psycopg2.connect(**params)
        if conn:
            print('CONNECTED TO DATABASE')
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            print("QUERY EXECUTION IS DONE")
            cursor.close()


def test(resp):
    pass

# Parameters of the PostgreSQL server connection
params = {
        "host" : "localhost",
        "database" : "data",
        "user" : "postgres",
        "password" : "vfrcfqvth",
        "port" : 5432
    }
# API list
api = ['https://p0c1rtf2ce.execute-api.eu-central-1.amazonaws.com/prod/e06990a6-2c04-4bb3-a5be-48ffea49f603',
       'https://p0c1rtf2ce.execute-api.eu-central-1.amazonaws.com/prod/22626fb7-dbbb-45ef-8787-f3bccbb2526b',
       'https://p0c1rtf2ce.execute-api.eu-central-1.amazonaws.com/prod/f07231f8-39bc-4133-b799-591665b166a9',
       'https://p0c1rtf2ce.execute-api.eu-central-1.amazonaws.com/prod/230ac88f-4186-482c-ac02-f3b93e618b03',
       'https://p0c1rtf2ce.execute-api.eu-central-1.amazonaws.com/prod/0919e6f9-d6cf-4b2c-9321-01b6f54054e3',
       'https://p0c1rtf2ce.execute-api.eu-central-1.amazonaws.com/prod/efba0291-d89f-4966-908a-97fb1afe7f26',
       'https://p0c1rtf2ce.execute-api.eu-central-1.amazonaws.com/prod/88ff105f-2dde-4541-a3d7-0d6143b5452c']


# Runs only once to create and grant!!!
# create_tables(params)
start = time.time()
main(api,params)
print(time.time()-start)