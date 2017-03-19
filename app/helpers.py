import pandas
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
    if row["GPS (Latitude)"] != None:
        return {
            "date":str(row.name).replace("T", " "),
            "latitude":row["GPS (Latitude)"],
            "longitude":row["GPS (Longitude)"]
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
    dist_traveled = haversine(gps_data['GPS (Longitude)'].shift(), gps_data['GPS (Latitude)'].shift(), 
          gps_data.ix[1:, 'GPS (Longitude)'], gps_data.ix[1:, 'GPS (Latitude)'])

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