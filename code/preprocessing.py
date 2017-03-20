import pandas as pd
import numpy as np

def preprocess(df,sample_rate="2s"):
    # drop some columns we don;t need
    df = df[['Acceleration (x)','Acceleration (y)','Acceleration (z)', 'Altimeter (Barometer) (Pressure)',\
             'Microphone (Left Channel Level)', 'Microphone (Right Channel Level)','Magnetometer (raw) (x)',\
             'Magnetometer (raw) (y)','Magnetometer (raw) (z)','Gyrometer (x)','Gyrometer (y)',\
             'Gyrometer (z)']]
    # drop the na values and convert everything to floats 
    df = df.dropna().astype(float)
    # Take the norm of the 3d values
    df['Acceleration'] =  np.sqrt(df['Acceleration (x)']**2 + df['Acceleration (y)']**2 + df['Acceleration (z)']**2)
    df['Magnetometer'] =  np.sqrt(df['Magnetometer (raw) (x)']**2 + df['Magnetometer (raw) (y)']**2 + df['Magnetometer (raw) (z)']**2)
    df['Gyrometer']    =  np.sqrt(df['Gyrometer (x)']**2 + df['Gyrometer (y)']**2 + df['Gyrometer (z)']**2)
    df['Microphone']   =  (df['Microphone (Left Channel Level)'] + df['Microphone (Right Channel Level)'])/2
    # drop the old column names
    df = df[['Acceleration','Magnetometer','Gyrometer','Microphone','Altimeter (Barometer) (Pressure)']]
    # resample the index, example of resampel rate is 2s
    df = df.resample(sample_rate).mean()
    return df   

