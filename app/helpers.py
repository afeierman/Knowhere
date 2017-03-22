import pandas as pd
import numpy as np

def query_db_convert_id(reader, collection, id_cols=None,
						sort_col=None, method=None, _filter={},
						username=None, sensor=None,
						min_date=None, max_date=None, include_max_date=False):
	if not method:
		df = reader.get_dataframe(collection=collection, filter_args=_filter).sort_values(sort_col)
	elif method == "unrolled":
		df = reader.get_dataframe_unrolled(collection=collection, filter_args=_filter).sort_values(sort_col)
	elif method == "pivoted":
		df = reader.get_dataframe_pivoted(collection=collection, username=username, sensor=sensor,
										min_date=min_date, max_date=max_date, include_max_date=include_max_date).sort_index()
	
	if method != "pivoted":
		for col in id_cols:
			df.ix[:,col] = df.ix[:,col].map(str)
	
	return df


# helper in converting dataframe to json array
def make_lat_long(row):
    if row["GPS Latitude"] != None:
        return {
            "date":str(row.name).replace("T", " "),
            "latitude":row["GPS Latitude"],
            "longitude":row["GPS Longitude"]
        }


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees, AKA Latitude / Longitude)

    All args must be of equal length.    

    """

    lon1 = lon1.astype(float)
    lat1 = lat1.astype(float)
    lon2 = lon2.astype(float)
    lat2 = lat2.astype(float)

    from math import radians, cos, sin, asin, sqrt

    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(np.radians,[lon1, lat1, lon2, lat2])

    #haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    miles = 3956 * c # Radius of earth in miles. Use 6370 for kilometers
    return miles


def set_distance_traveled(gps_data, json_array):
    """
    Calculate the distance a user has traveled over a given date range. Involves all modes of transportation, 
    and is calculated using Great-circle distance.
    """

    #Use haversine function to get distances between all GPS points
    dist_traveled = haversine(gps_data['GPS Longitude'].shift(), gps_data['GPS Latitude'].shift(), 
          gps_data.ix[1:, 'GPS Longitude'], gps_data.ix[1:, 'GPS Latitude'])

    json_array.append({"total_distance": dist_traveled.sum()})


# def distance_traveled(min_date, max_date, username):
#     """
#     Calculate the distance a user has traveled over a given date range. Involves all modes of transportation, 
#     and is calculated using Great-circle distance.
#     """
    
#     #make DB query to get GPS data for specified day 
#     day_dist = reader.get_dataframe_pivoted(collection = 'iphone_test', sensor = "GPS", username = username,
#                                 min_date = str(min_date), max_date = str(max_date))
#     day_dist = day_dist.astype(float)
    
#     #Use haversine function to get distances between all GPS points
#     dist_traveled = haversine(day_dist['GPS (Longitude)'].shift(), day_dist['GPS (Latitude)'].shift(), 
#           day_dist.ix[1:, 'GPS (Longitude)'], day_dist.ix[1:, 'GPS (Latitude)'])
    
#     return dist_traveled.sum()


def get_locs(reader, user_data, user_name, json_array):
    """
    Predict clusters from cluster
    """
    from sklearn import preprocessing
    from sklearn.cluster import AgglomerativeClustering

    #H_model = uploader.retrieve_from_s3(user_name, model_type='H', bucket='knowhere-data', collection='models')
    H_model = get_model(user_name)
    H_data = user_data[['GPS Altitude','GPS Latitude','GPS Longitude']]
    preprocess = preprocessing.scale(H_data)
    clusters = H_model.fit_predict(H_data)
    H_data.reset_index(inplace=True)

    H_data["ymdh"] = H_data["index"].apply(lambda t: "{year}{month}{day}{hour}".format(
        year=t.year, month=t.month, day=t.day, hour=t.hour
    ))
    H_data["hour"] = H_data["index"].apply(lambda t: t.hour)
    H_data["cluster"] = pd.Series(clusters)
    H_data.loc[:,"GPS Latitude"] = H_data["GPS Latitude"].astype(float)
    H_data.loc[:,"GPS Longitude"] = H_data["GPS Longitude"].astype(float)
    H_data.loc[:,"GPS Altitude"] = H_data["GPS Altitude"].astype(float)
    #df_grouped = H_data.groupby(["cluster", "hour"]).median()

    #print "DF_GROUPED: ", df_grouped

    get_label_latlongs(H_data, json_array)


def get_label_latlongs(df, json_array):
    df_grouped = df.groupby(["cluster", "hour"]).median()
    zero = df_grouped.loc[0,:]
    one = df_grouped.loc[1,:]
    labels = {"home":{},"work":{}}
    home=None; work=None

    gb = df.groupby(["cluster"]).agg(
        {"hour": lambda x: float(((2 <= x) & (x < 6)).sum())/((0 <= x) & (x < 24)).sum()}
    )

    home_idx = gb[gb["hour"] == max(gb["hour"])].index[0]

    # if np.mean(zero.index) < np.mean(one.index):
    #     home,work = one,zero
    # else:
    #     home,work = zero,one

    if home_idx != 0:
        (home, work) = (one, zero)
    else:
        (home, work) = (zero, one)

    print "150", "\n\n", work, "\n\n", work.index

    min_home = home.loc[home.index == min(home.index),:]
    min_work = work.loc[work.index == work.index[len(work.index)/2],:]

    print "155", "\n\n", min_home, "\n\n", min_work

    labels["home"]["lat"] = float(min_home["GPS Latitude"])
    labels["home"]["long"] = float(min_home["GPS Longitude"])
    labels["work"]["lat"] = float(min_work["GPS Latitude"])
    labels["work"]["long"] = float(min_work["GPS Longitude"])

    print "LABELS", labels

    json_array.append(labels)


def get_model(username):
    import pickle
    filename = "data/hclust_{0}.p".format(username)
    return pickle.load(open(filename, "rb" ))