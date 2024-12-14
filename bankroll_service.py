import datetime
import json
import os


from flask import Flask, request, jsonify

app = Flask(__name__)

# Check if running inside Docker
if os.path.exists("/.dockerenv"):
    # Running inside Docker, use the volume-mounted directory
    BANKROLL_FILE = "/app/data/finances.json"
else:
    # Running locally, use the current working directory
    BANKROLL_FILE = "finances.json"


def create_file():
    if not os.path.exists(BANKROLL_FILE):
        with open(BANKROLL_FILE, "w") as f:
            json.dump({}, f)


def read_file():
    with open(BANKROLL_FILE, "r") as f:
        bankroll_db = json.load(f)
    return bankroll_db


def write_to_file(bankroll_db):
    with open(BANKROLL_FILE, "w") as f:
        json.dump(bankroll_db, f, indent=4)


def create_user_entry(user):
    data = read_file()
    data[user] = {"balance": 0, "transactions": []}
    write_to_file(data)


@app.route("/get-balance", methods=["GET"])
def get_balance():
    try:
        data = read_file()
    except FileNotFoundError:
        create_file()
        data = read_file()
    username = request.args.get("username")
    if username not in data:
        create_user_entry(username)
        data = read_file()
    balance = data[username].get("balance", 0)
    return jsonify({"username": username, "balance": balance}), 200


@app.route("/post-transcation", methods=["POST"])
def post_transcation():
    try:
        data = read_file()
    except FileNotFoundError:
        create_file()
        data = read_file()
    request_data = request.json
    username = request_data.get("username")
    withdrawals = request_data.get("withdrawals", 0)
    deposits = request_data.get("deposits", 0)
    transaction_date = request_data.get("date")
    if username not in data:
        create_user_entry(username)
        data = read_file()
    balance = data[username].get("balance", 0)
    balance += deposits
    if withdrawals > balance:
        withdrawals = balance
    balance -= withdrawals
    transaction = {
        "date": transaction_date,
        "withdrawals": withdrawals,
        "deposits": deposits,
    }
    data[username]["balance"] = balance
    data[username].setdefault("transactions", []).append(transaction)
    write_to_file(data)
    return (
        jsonify({"message": "Transaction successful", "new_balance": balance}),
        200,
    )


@app.route("/get-transcations", methods=["GET"])
def get_transactions():
    username = request.args.get("username")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    finances = read_file()

    try:
        user_transcations = finances.get(username)["transactions"]
    except TypeError:
        return jsonify({"error": "No transcations found for this user"}), 404
    if len(user_transcations) == 0:
        return jsonify({"error": "No transcations found for this user"}), 404

    if start_date and end_date:
        start_date = datetime.datetime.strptime(start_date, "%m/%d/%y")
        end_date = datetime.datetime.strptime(end_date, "%m/%d/%y")
        filtered_transactions = [
            transaction
            for transaction in user_transcations
            if start_date
            <= datetime.datetime.strptime(transaction["date"], "%m/%d/%y")
            <= end_date
        ]
        return jsonify(filtered_transactions), 200

    return jsonify(user_transcations), 200


@app.route("/delete-finances", methods=["DELETE"])
def delete_finances():
    try:
        data = read_file()
    except FileNotFoundError:
        create_file()
        data = read_file()
    username = request.args.get("username")
    if username not in data:
        create_user_entry(username)
        data = read_file()
    del data[username]
    write_to_file(data)
    return (
        jsonify(
            {"message": f"Finances for user {username} have been deleted."}
        ),
        200,
    )


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8082)
