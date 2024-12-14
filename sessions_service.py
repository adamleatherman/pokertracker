import datetime
import json
import os

from flask import Flask, request, jsonify

app = Flask(__name__)


# Check if running inside Docker
if os.path.exists("/.dockerenv"):
    # Running inside Docker, use the volume-mounted directory
    FILE_PATH = "/app/data/sessions.json"
else:
    # Running locally, use the current working directory
    FILE_PATH = "sessions.json"


@app.route("/add-session", methods=["POST"])
def add_session():
    data = request.json
    username = data.get("username")
    date = data.get("date")
    length = data.get("length")
    stakes = data.get("stakes")
    buyin = data.get("buyin")
    cashout = data.get("cashout")
    location = data.get("location", "")
    notes = data.get("notes", "")
    notable_hands = data.get("notable_hands", "")

    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, "w") as f:
            json.dump({}, f)

    with open(FILE_PATH, "r") as f:
        sessions_db = json.load(f)

    new_session = {
        "date": date,
        "length": length,
        "stakes": stakes,
        "buyin": buyin,
        "cashout": cashout,
        "location": location,
        "notes": notes,
        "notable_hands": notable_hands,
    }

    if username in sessions_db:
        sessions_db[username].append(new_session)
    else:
        sessions_db[username] = [new_session]

    with open(FILE_PATH, "w") as file:
        json.dump(sessions_db, file, indent=4)

    return jsonify({"message": f"Session added for user {username}"}), 201


@app.route("/get-sessions", methods=["GET"])
def get_sessions():
    username = request.args.get("username")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    print(start_date, type(start_date))
    print(end_date, type(end_date))

    with open(FILE_PATH, "r") as f:
        sessions_db = json.load(f)

    user_sessions = sessions_db.get(username)
    if not user_sessions:
        return jsonify({"error": "No sessions found for this user"}), 404

    if start_date and end_date:
        start_date = datetime.datetime.strptime(start_date, "%m/%d/%y")
        end_date = datetime.datetime.strptime(end_date, "%m/%d/%y")
        filtered_sessions = [
            session
            for session in user_sessions
            if start_date
            <= datetime.datetime.strptime(session["date"], "%m/%d/%y")
            <= end_date
        ]
        return jsonify(filtered_sessions), 200

    return jsonify(user_sessions), 200


@app.route("/delete-sessions", methods=["DELETE"])
def delete_sessions():
    username = request.args.get("username")

    with open(FILE_PATH, "r") as f:
        sessions_db = json.load(f)

    del sessions_db[username]

    with open(FILE_PATH, "w") as file:
        json.dump(sessions_db, file, indent=4)

    return (
        jsonify(
            {"message": f"Sessions for user {username} have been deleted."}
        ),
        200,
    )


if __name__ == "__main__":
    app.run(debug=True, port=8081)
