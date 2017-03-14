import pandas as pd
from re import search
from bson import ObjectId
from datetime import datetime
from db.knowhere_db import Reader


def iphone(file_with_path, username, dir_to_aggregate=None):       
    df = read_from_csvs(username, file_with_path, dir_to_aggregate)
    df = clean_iphone_data(df)
    df = aggregate_data(df)
    return df

def andoid(file_with_path, username, dir_to_aggregate=None):
    raise Exception('Android processing not yet implemented')
    df = pd.DataFrame()
    #df = read_from_csvs(username, file_with_path, dir_to_aggregate)
    #df = clean_android_data(df)
    #df = aggregate_data(df)
    #df['user_id'] = user_id
    return df
    

def get_user_id(df, username):
    reader = Reader('knowhere')
    user_data = reader.filter_collection('users', {'username': username}, find_one=True)
    user_id = user_data.get('_id') if user_data is not None else None
    if user_id is None:
        raise Exception('Could not get id for user {}'.format(username))
    df['user_id'] = user_id
    return df

    
def read_from_csvs(username, file_with_path, dir_to_aggregate=None):
    if dir_to_aggregate is not None:
        aggregate_csvs(username, dir_to_aggregate, file_with_path)
    df = read_single_csv(file_with_path)
    df = get_user_id(df, username)
    return df
  
  
def read_single_csv(file_with_path):
    df = pd.read_csv(file_with_path, sep=', ', index_col=0, skiprows=0, engine='python', thousands=',', skip_blank_lines=False)
    df.index = pd.to_datetime(df.index.str.replace('"',''))
    return df
    
    
def aggregate_csvs(username, csv_dir, file_with_path):
    from glob import glob
    with open(file_with_path, 'w+') as f_handler:
        f_handler.write('timestamp, sensor, data_name, data_display, data_raw\n')
        for fn in glob(csv_dir + r'\*{}*'.format(username)):
            with open(fn, 'r+') as f:
                next(f)
                for line in f:
                    # get rid of bad lines
                    if not search('Screen', line):
                        f_handler.write(line)
    
    
def clean_iphone_data(df):
    df = df.applymap(lambda x: str.strip(x) if type(x)==str else x)
    #df = df.applymap(lambda x: pd.to_numeric(x, errors='ignore'))
	# drop some data we don't need or want
    df = df[df.data_name != 'Enabled']
    df = df[df.data_name != 'Authorisation Status']
    df = df[df.data_name != 'Floor']
    df = df[df.sensor != 'Accelerometer (raw)']
    df = df[df.sensor != 'Gyrometer (raw)']
    df = df[df.sensor != 'Acceleration (total)']
    # Rename some sensor data so it's easier to deal with
    df.replace(to_replace={'sensor': {'Acceleration (via Gravity)': 'Gravity', 
                                      'Acceleration (via User)': 'Acceleration',
									  'Gyrometer (smooth)': 'Gyrometer',
									  'Magnetometer (corrected for device)': 'Magnetometer'
									  }
						}, inplace=True)
    return df

def aggregate_data(df):
    df = df.filter(items=['user_id', 'sensor', 'data_name', 'data_raw'])
    # group by some columns to join the others
    df = df.groupby([df.index, 'user_id', 'sensor']).agg(lambda x: tuple(x))
    # above function makes user_id and sensor indexs, so undo this
    df = df.reset_index(level=['user_id', 'sensor'])
    df['data'] = df.apply(lambda row: {name: value for name, value in zip(row['data_name'], row['data_raw'])}, axis=1)
    df = df.reset_index(level=0)
    df.timestamp = pd.to_datetime(df.timestamp)
    df = df.filter(items=['timestamp', 'user_id', 'sensor', 'data'])	
    df.user_id = df.user_id.apply(ObjectId)
    return df
    