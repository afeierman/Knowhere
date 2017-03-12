from flask import Flask, send_file
import json

app = Flask(__name__)

@app.route("/")
def index():
    return send_file("templates/knowhere.html")

@app.route("/get_unique_users", methods=["GET"])
def get_unique_users():
	return json.dumps([{"names":["Andrew", "Bill", "Emil", "Glen"]}])

	
if __name__ == "__main__":
    app.run(host='0.0.0.0')