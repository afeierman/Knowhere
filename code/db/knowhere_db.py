import warnings
import pymongo
import ConfigParser
import pandas as pd
from bson.objectid import ObjectId
from dateutil.parser import parse as parse_date

class Reader:

    def __init__(self, db_name='test'):
        parser = ConfigParser.RawConfigParser()
        parser.read('credentials.cfg')
        self.ip = parser.get('server', 'ip')
        self.user = parser.get('Reader', 'user')
        self.pwd = parser.get('Reader', 'pwd')
        self.db_name = db_name
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        connect_string = "mongodb://{user}:{pwd}@{ip}/{db_name}".format(user=self.user, pwd=self.pwd,
                                                                        ip=self.ip, db_name=self.db_name)
        self.client = pymongo.MongoClient(connect_string)
        self.db = self.client[self.db_name]   
        
    def build_filter(self, username=None, user_id=None, sensor=None, min_date=None, max_date=None, include_max_date=False): 
        filter_args = {}
        if username:
            user_data = self.filter_collection('users', filter_args={'username': username}, find_one=True)
            if user_data:
                user_id = user_data.get('_id')
        if user_id:
            filter_args['user_id'] = user_id            
        if sensor:
            filter_args['sensor'] = sensor
        if min_date or max_date:
            date_filter = {}
            if min_date:
                date_filter['$gte'] = parse_date(min_date)
            if max_date:
                if include_max_date:
                    date_filter['$lte'] = parse_date(max_date)
                else:
                    date_filter['$lt'] = parse_date(max_date)
            filter_args['timestamp'] = date_filter
        return filter_args
        
    def filter_collection(self, collection, filter_args={}, find_one=False):
        if find_one:
            return self.db[collection].find_one(filter_args)
        return self.db[collection].find(filter_args)

    def get_dataframe(self, collection, filter_args={}):
        data = [entry for entry in self.filter_collection(collection, filter_args)]
        return pd.DataFrame(data)
        
    def get_dataframe_unrolled(self, collection, username=None, user_id=None, sensor=None, min_date=None, max_date=None, include_max_date=False):
        # build filter_args
        filter_args = self.build_filter(username, user_id, sensor, min_date, max_date, include_max_date)
        data = []
        for entry in self.filter_collection(collection, filter_args):
            for data_name, data_raw in entry['data'].iteritems():
                row = {'timestamp': entry['timestamp'], 'user_id': entry['user_id'], 'sensor': entry['sensor']}
                row['data_name'] = data_name
                row['data_raw'] = data_raw
                data.append(row)
        return pd.DataFrame(data)
        
    def get_dataframe_pivoted(self, collection, username=None, user_id=None, sensor=None, min_date=None, max_date=None, include_max_date=False):
        # build filter_args
        filter_args = self.build_filter()
        if not user_id and not username:
            warnings.warn('Excluding user_id from filter can cause errors during pivot', Warning)
        # get the unrolled version so we can pivot the dataframe
        rdf = self.get_dataframe_unrolled(collection, username, user_id, sensor, min_date, max_date, include_max_date)
        #rdf.timestamp = pd.to_datetime(rdf.timestamp)
        rdf['sensor_name'] = rdf.apply(lambda row: row.sensor + ' (' + row.data_name + ')', axis=1)
        rdf.drop(['sensor', 'data_name'], axis=1, inplace=True)
        rdf_pivoted = rdf.pivot(index='timestamp', columns='sensor_name', values='data_raw')
        return rdf_pivoted
            
    def close(self):
        self.client.close()


class Writer(Reader):

    def __init__(self, db_name='test'):
        parser = ConfigParser.RawConfigParser()
        parser.read('credentials.cfg')
        self.ip = parser.get('server', 'ip')
        self.user = parser.get('Writer', 'user')
        self.pwd = parser.get('Writer', 'pwd')
        self.db_name = db_name
        self.client = None
        self.db = None
        self.connect()

    def write_dataframe_to_collection(self, df, collection):
        data_to_insert = df.to_dict(orient='records')
        self.db[collection].insert_many(data_to_insert)