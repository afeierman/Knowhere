import pandas as pd
from bson import ObjectId
from datetime import datetime


def iphone(user_id, file_with_path):
    df = read_csv(user_id, file_with_path)
    df = clean_iphone_data(df)
    df = aggregate_data(df)
    return df
		

def read_csv(user_id, file_with_path):
    df = pd.read_csv(file_with_path, sep=', ', index_col=0, skiprows=0, engine='python', thousands=',', skip_blank_lines=False)
    df.index = pd.to_datetime(df.index.str.replace('"',''))
    df['user_id'] = user_id
    return df
    
    
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
    #df.data_raw = df.data_raw.map(lambda x: pd.to_numeric(x, errors='ignore', downcast='float'))
    return df
    

def aggregate_data(df):
    df = df.filter(items=['user_id', 'sensor', 'data_name', 'data_raw'])
    # group by some columns to join the others
    df = df.groupby([df.index, 'user_id','sensor']).agg(lambda x: tuple(x))
    # above function makes user_id and sensor indexs, so undo this
    df = df.reset_index(level=['user_id', 'sensor'])
    df['data'] = df.apply(lambda row: {name: value for name, value in zip(row['data_name'], row['data_raw'])}, axis=1)
    df = df.reset_index(level=0)
    df.timestamp = pd.to_datetime(df.timestamp)
    df = df.filter(items=['timestamp', 'user_id', 'sensor', 'data'])	
    df.user_id = df.user_id.apply(ObjectId)
    return df