import pandas

def query_db_convert_id(reader, collection, id_cols=None,
						sort_col=None, method=None, _filter={}):
	if not method:
		df = reader.get_dataframe(collection, _filter).sort_values(sort_col)
	elif method == "unrolled":
		df = reader.get_dataframe_unrolled(collection, _filter).sort_values(sort_col)
	elif method == "pivoted":
		df = reader.get_dataframe_pivoted(collection, _filter).sort_index()
	
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