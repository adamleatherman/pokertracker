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


def create_file():
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, "w") as f:
            json.dump({}, f)


def read_file():
    with open(FILE_PATH, "r") as f:
        sessions = json.load(f)
    return sessions


def write_to_file(sessions):
    with open(FILE_PATH, "w") as f:
        json.dump(sessions, f, indent=4)


@app.route("/get-average-lengths", methods=["GET"])
def get_average_length_by_stake():
    if not os.path.exists(FILE_PATH):
        return jsonify({"error": "No sessions found for this user"}), 404
    username = request.args.get("username")
    sessions = read_file()
    if username not in sessions:
        return jsonify({"error": "No sessions found for this user"}), 404
    user_sessions = sessions[username]
    if len(user_sessions) == 0:
        return jsonify({"error": "No sessions found for this user"}), 404
    stake_lengths = {}
    for session in user_sessions:
        stake = session.get("stakes")
        length = session.get("length")
        if stake and length:
            length_in_hours = length / 60
            if stake not in stake_lengths:
                stake_lengths[stake] = {"total_length": 0, "count": 0}
            stake_lengths[stake]["total_length"] += length_in_hours
            stake_lengths[stake]["count"] += 1
    average_lengths = {}
    for stake, data in stake_lengths.items():
        average_length = data["total_length"] / data["count"]
        average_lengths[stake] = round(average_length, 2)
    return jsonify(average_lengths), 200


@app.route("/get-winrates", methods=["GET"])
def get_winrate_by_stake():
    if not os.path.exists(FILE_PATH):
        return jsonify({"error": "No sessions found for this user"}), 404
    username = request.args.get("username")
    sessions = read_file()
    if username not in sessions:
        return jsonify({"error": "No sessions found for this user"}), 404
    user_sessions = sessions[username]
    if len(user_sessions) == 0:
        return jsonify({"error": "No sessions found for this user"}), 404
    winrates_by_stake = {}
    for session in user_sessions:
        stake = session["stakes"]
        buyin = session["buyin"]
        cashout = session["cashout"]
        length = session["length"]
        winrate = cashout - buyin
        if stake not in winrates_by_stake:
            winrates_by_stake[stake] = {"total_winrate": 0, "total_hours": 0}
        winrates_by_stake[stake]["total_winrate"] += winrate
        winrates_by_stake[stake]["total_hours"] += length / 60
    total_winrates_by_stake = {}
    for stake, data in winrates_by_stake.items():
        if data["total_hours"] > 0:
            total_winrate = data["total_winrate"] / data["total_hours"]
            total_winrates_by_stake[stake] = round(total_winrate, 2)
    return jsonify(total_winrates_by_stake), 200


if __name__ == "__main__":
    app.run(debug=True, port=8083)
