from flask import Blueprint, request, jsonify
from datetime import datetime
from app.extensions import collection

webhook = Blueprint("webhook", __name__)

@webhook.route("/reciver", methods=["POST"])
def github_webhook():
    payload = request.json
    event_type = request.headers.get("X-GitHub-Event")
    action = payload.get("action")

    data = {
        "event_type": event_type,
        "action": action,
        "author": None,
        "from_branch": None,
        "to_branch": None,
        "request_id": None,
        "timestamp": datetime.utcnow(),
        "raw_payload": payload
    }

    if event_type == "push":
        data.update({
            "action": "PUSH",
            "request_id": payload.get("after"),
            "author": payload.get("pusher", {}).get("name"),
            "to_branch": payload.get("ref", "").split("/")[-1]
        })

    elif event_type == "pull_request":
        pr = payload.get("pull_request", {})

        data.update({
            "request_id": pr.get("id"),
            "author": pr.get("user", {}).get("login"),
            "from_branch": pr.get("head", {}).get("ref"),
            "to_branch": pr.get("base", {}).get("ref")
        })

    elif event_type == "pull_request_review":
        review = payload.get("review", {})
        pr = payload.get("pull_request", {})

        data.update({
            "request_id": review.get("id"),
            "author": review.get("user", {}).get("login"),
            "from_branch": pr.get("head", {}).get("ref"),
            "to_branch": pr.get("base", {}).get("ref")
        })

    elif event_type == "pull_request_review_comment":
        comment = payload.get("comment", {})
        pr = payload.get("pull_request", {})

        data.update({
            "request_id": comment.get("id"),
            "author": comment.get("user", {}).get("login"),
            "from_branch": pr.get("head", {}).get("ref"),
            "to_branch": pr.get("base", {}).get("ref")
        })

    elif event_type == "pull_request_review_thread":
        thread = payload.get("thread", {})
        pr = payload.get("pull_request", {})

        data.update({
            "request_id": thread.get("id"),
            "author": payload.get("sender", {}).get("login"),
            "from_branch": pr.get("head", {}).get("ref"),
            "to_branch": pr.get("base", {}).get("ref")
        })

    elif event_type == "merge_group":
        data.update({
            "request_id": payload.get("merge_group", {}).get("head_sha"),
            "author": payload.get("sender", {}).get("login"),
            "to_branch": payload.get("merge_group", {}).get("base_ref")
        })

    else:
        return jsonify({"message": "Event ignored"}), 200

    result = collection.insert_one(data)
    data["_id"] = str(result.inserted_id)

    return jsonify({
        "message": "Event stored",
        "event_type": event_type,
        "action": action,
        "data": data
    }), 200

@webhook.route("/events", methods=["GET"])
def get_events():
    events = []
    for doc in collection.find().sort("timestamp", -1):
        doc["_id"] = str(doc["_id"])
        events.append(doc)
    return jsonify(events), 200


@webhook.route("/events/<action>", methods=["GET"])
def get_events_by_action(action):
    events = []
    for doc in collection.find({"action": action.upper()}).sort("timestamp", -1):
        doc["_id"] = str(doc["_id"])
        events.append(doc)
    return jsonify(events), 200
