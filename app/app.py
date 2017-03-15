# Python
from flask import Flask, send_file, request
import json
import pandas as pd

# User-created
import knowhere_db as kdb
from helpers import *

reader = kdb.Reader(db_name='knowhere')
users = query_db_convert_id(
	reader=reader,
	collection="users",
	id_cols=["_id"],
	sort_col="username",
	method=False,
	_filter={}
)

"""
will get every user's data the when the app is run.
need to make this dynamic so new records are fetched
"""
# data = query_db_convert_id(
# 	reader=reader,
# 	collection="iphone_test",
# 	id_cols=["_id", "user_id"],
# 	sort_col="timestamp",
# 	unrolled=True
# )



app = Flask(__name__)

@app.route("/")
def index():
    return send_file("templates/knowhere.html")

@app.route("/query_users", methods=["GET"])
def get_users():
	return json.dumps(users.to_dict(orient='records'));
	#return json.dumps([{"names":["Andrew", "Bill", "Emil", "Glen"]}])

@app.route("/query_iphone_test", methods=["GET"])
def get_iphone_test():
	user_id = request.args.get("user_id")
	print user_id
	temp_data = query_db_convert_id(
		reader=reader,
		collection="iphone_test",
		id_cols=None,
		sort_col=None,
		method="pivoted",
		_filter={"user_id":kdb.ObjectId(user_id)}
	)

	# just getting lat/long for testing
	user_data = temp_data.apply(make_lat_long, axis=1)
	user_data = list(user_data[pd.notnull(user_data)])
	return json.dumps(user_data);
	#return json.dumps([{"names":["Andrew", "Bill", "Emil", "Glen"]}])
	
@app.teardown_appcontext
def close_db(error):
	reader.close()


if __name__ == "__main__":
    app.run(host='0.0.0.0')