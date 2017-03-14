import pymongo
import ConfigParser
import pandas as pd
from bson.objectid import ObjectId


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

    def filter_collection(self, collection, filter_args={}, find_one=False):
        if find_one:
            return self.db[collection].find_one(filter_args)
        return self.db[collection].find(filter_args)

    def get_dataframe(self, collection, filter_args={}):
        data = [entry for entry in self.filter_collection(collection, filter_args)]
        return pd.DataFrame(data)
        
    def get_dataframe_unrolled(self, collection, filter_args={}):
        data = []
        if 'user_id' in filter_args.keys():
            filter_args['user_id'] = ObjectId(filter_args['user_id'])
        for entry in self.filter_collection(collection, filter_args):
            for data_name, data_raw in entry['data'].iteritems():
                row = {'timestamp': entry['timestamp'], 'user_id': entry['user_id'], 'sensor': entry['sensor']}
                row['data_name'] = data_name
                row['data_raw'] = data_raw
                data.append(row)
        return pd.DataFrame(data)
        
    def get_dataframe_pivoted(self, collection, filter_args={}):
        import warnings
        if 'user_id' not in filter_args.keys():
            warnings.warn('Excluding user_id from filter can cause errors during pivot', Warning)
        rdf = self.get_dataframe_unrolled(collection, filter_args)
        rdf.timestamp = pd.to_datetime(rdf.timestamp)
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