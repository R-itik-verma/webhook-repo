from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Set up MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['github_events']  # Create a database called "github_events"
collection = db['events']  # Collection to store GitHub events

# Webhook endpoint to receive GitHub actions
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    # Store necessary data in MongoDB
    event_data = {
        "action": request.headers.get('X-GitHub-Event'),
        "author": data.get('sender', {}).get('login'),
        "from_branch": data.get('pull_request', {}).get('head', {}).get('ref', ''),
        "to_branch": data.get('ref'),
        "timestamp": datetime.utcnow()  # Store the time the event was received
    }
    collection.insert_one(event_data)  # Save to MongoDB
    return jsonify({"status": "success"}), 200

# API endpoint to fetch events for the UI
@app.route('/events', methods=['GET'])
def get_events():
    # Fetch latest events (within the last 15 seconds) from MongoDB
    events = list(collection.find().sort("timestamp", -1).limit(10))
    return jsonify(events), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
