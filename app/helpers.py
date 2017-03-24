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


def set_distance(gps_data, json_array):
    """
    Calculate the distance a user has traveled over a given date range. Involves all modes of transportation, 
    and is calculated using Great-circle distance.
    """

    import pandas.tseries.offsets as pdo

    hourly_distances = [('Date', 'Distance')]

    #Use haversine function to get distances between all GPS points
    dist_traveled = haversine(gps_data['GPS Longitude'].shift(), gps_data['GPS Latitude'].shift(), 
          gps_data.ix[1:, 'GPS Longitude'], gps_data.ix[1:, 'GPS Latitude'])


    dist_grouped = dist_traveled.groupby(pd.Grouper(freq='1H')).sum()
    
    for ts, dist in dist_grouped.iteritems():
        h = "{0:02}-{1:02}-{2:02} {3:02}:{4:02}:{5:02}".format(
            ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second
        )

        if np.isnan(dist):
            dist = 0

        hourly_distances.append((h, dist))

    json_array.append({"total_distance": dist_traveled.sum()})
    json_array.append({"hourly_distances":hourly_distances})


def get_locs(reader, user_data, user_name, json_array):
    """
    Predict clusters from cluster
    """
    from sklearn import preprocessing
    from sklearn.cluster import AgglomerativeClustering

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

    get_label_latlongs(H_data, json_array)


def get_label_latlongs(df, json_array):
    df_grouped = df.groupby(["cluster", "hour"]).median()
    zero = df_grouped.loc[0,:]; one = df_grouped.loc[1,:]
    zero_full = df[df.cluster==0]; one_full = df[df.cluster==1]
    labels = {"home":{},"work":{}}
    home=None; work=None
    home_full=None; work_full=None

    gb = df.groupby(["cluster"]).agg(
        {"hour": lambda x: float(((0 <= x) & (x < 6)).sum())/((0 <= x) & (x < 24)).sum()}
    )

    home_idx = gb[gb["hour"] == max(gb["hour"])].index[0]


    if home_idx != 0:
        (home, work) = (one, zero)
        (home_full, work_full) = (one_full, zero_full)
    else:
        (home, work) = (zero, one)
        (home_full, work_full) = (zero_full, one_full)

    set_loc_percents(home_full, work_full, json_array)

    min_home = home.loc[home.index == min(home.index),:]
    min_work = work.loc[work.index == work.index[len(work.index)/2],:]

    labels["home"]["lat"] = float(min_home["GPS Latitude"])
    labels["home"]["long"] = float(min_home["GPS Longitude"])
    labels["work"]["lat"] = float(min_work["GPS Latitude"])
    labels["work"]["long"] = float(min_work["GPS Longitude"])

    json_array.append(labels)


def get_model(username):
    import pickle
    filename = "data/hclust_{0}.p".format(username)
    return pickle.load(open(filename, "rb" ))


def set_loc_percents(home, work, json_array):
    home = home.groupby(lambda x: home['index'][x].day).agg({"index": lambda i: (max(i)-min(i)).total_seconds()})
    work = work.groupby(lambda x: work['index'][x].day).agg({"index": lambda i: (max(i)-min(i)).total_seconds()})
    # datediff_home = max(home["index"]) - min(home["index"])
    # datediff_work = max(work["index"]) - min(work["index"])
    seconds_home = np.sum(home["index"])
    seconds_work = np.sum(work["index"])
    seconds_total = seconds_home + seconds_work
    percent_home = round(100*(float(seconds_home) / seconds_total), 2)
    percent_work = round(100*(float(seconds_work) / seconds_total), 2)

    json_array.append({"percent_home":percent_home, "percent_work":percent_work})

