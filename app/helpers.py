import pandas

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


def make_lat_long(row):
    if row["GPS (Latitude)"] != None:
        return {
            "date":str(row.name).replace("T", " "),
            "latitude":row["GPS (Latitude)"],
            "longitude":row["GPS (Longitude)"]
        }