import hashlib
import json
import os

from flask import Flask, request, jsonify

app = Flask(__name__)


def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

        # Check if running inside Docker
    if os.path.exists("/.dockerenv"):
        # Running inside Docker, use the volume-mounted directory
        users_file = "/app/data/users.json"
    else:
        # Running locally, use the current working directory
        users_file = "users.json"

    if not os.path.exists(users_file):
        with open(users_file, "w") as f:
            json.dump({}, f)

    with open(users_file, "r") as f:
        user_db = json.load(f)

    if username in user_db:
        return jsonify({"error": "User already exists"}), 409

    hashed_password = hash_password(password)
    user_db[username] = hashed_password

    with open(users_file, "w") as f:
        json.dump(user_db, f, indent=4)

    return jsonify({"message": "User registered successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if os.path.exists("/.dockerenv"):
        # Running inside Docker, use the volume-mounted directory
        users_file = "/app/data/users.json"
    else:
        # Running locally, use the current working directory
        users_file = "users.json"

    if not os.path.exists(users_file):
        return (
            jsonify(
                {"error": "No user database found. Please register first."}
            ),
            404,
        )

    with open(users_file, "r") as f:
        user_db = json.load(f)

    stored_password = user_db.get(username)
    if not stored_password or stored_password != hash_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({"message": "Login successful"}), 200


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
