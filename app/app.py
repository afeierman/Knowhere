# Python
from flask import Flask, send_file
import json

# User-created
import knowhere_db as kdb

reader = kdb.Reader(db_name='knowhere')
users = reader.get_dataframe('users').sort_values("username")

app = Flask(__name__)

@app.route("/")
def index():
    return send_file("templates/knowhere.html")

@app.route("/get_users", methods=["GET"])
def get_users():
	temp = users.drop("_id", axis=1)
	return json.dumps(temp.to_dict(orient='records'));
	#return json.dumps([{"names":["Andrew", "Bill", "Emil", "Glen"]}])
	
@app.teardown_appcontext
def close_db(error):
	reader.client.close()


if __name__ == "__main__":
    app.run(host='0.0.0.0')