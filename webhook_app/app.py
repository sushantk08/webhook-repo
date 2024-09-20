from flask import Flask,request,jsonify, render_template
from pymongo.mongo_client import MongoClient
from datetime import datetime

app=Flask(__name__)
client=MongoClient("mongodb+srv://kulkarnisushant87:test234!!@actions.yoer5.mongodb.net/?retryWrites=true&w=majority&appName=actions")
db = client.github_events
collection = db.events

@app.route('/')
def index():
    events = list(collection.find({}, {'_id': 0}))
    return render_template('index.html', events=events)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        # Parse the event type
        event_type = request.headers.get('X-GitHub-Event', 'ping')

        if event_type == 'push':
            author = data['pusher']['name']
            to_branch = data['ref'].split('/')[-1]
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            event = {"author": author, "action": "pushed", "to_branch": to_branch, "timestamp": timestamp}

        elif event_type == 'pull_request':
            author = data['pull_request']['user']['login']
            from_branch = data['pull_request']['head']['ref']
            to_branch = data['pull_request']['base']['ref']
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            event = {"author": author, "action": "submitted a pull request", "from_branch": from_branch, "to_branch": to_branch, "timestamp": timestamp}

        elif event_type == 'pull_request' and data['action'] == 'closed' and data['pull_request']['merged']:
            author = data['pull_request']['user']['login']
            from_branch = data['pull_request']['head']['ref']
            to_branch = data['pull_request']['base']['ref']
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            event = {"author": author, "action": "merged branch", "from_branch": from_branch, "to_branch": to_branch, "timestamp": timestamp}

        else:
            return jsonify({"message": "Event type not handled"}), 400

        collection.insert_one(event)
        return jsonify({"message": "Event received"}), 200

if __name__=="__main__":
    app.run(debug=True)