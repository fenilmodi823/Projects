from flask import Flask, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for all routes

# ISS API from Open Notify
ISS_API = "http://api.open-notify.org/iss-now.json"

@app.route("/iss-location", methods=["GET"])
def get_iss_location():
    response = requests.get(ISS_API)
    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({"error": "Failed to fetch ISS location"}), 500

if __name__ == "__main__":
    app.run(debug=True)
