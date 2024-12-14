import getpass
import json
import os
import requests
import sys
from datetime import datetime

USERS_URL = (
    "http://users_service:8080"
    if os.path.exists("/.dockerenv")
    else "http://127.0.0.1:8080"
)
SESSIONS_URL = (
    "http://sessions_service:8081"
    if os.path.exists("/.dockerenv")
    else "http://127.0.0.1:8081"
)
BANKROLL_URL = (
    "http://bankroll_service:8082"
    if os.path.exists("/.dockerenv")
    else "http://127.0.0.1:8082"
)
STATISTICS_URL = (
    "http://statistics_service:8083"
    if os.path.exists("/.dockerenv")
    else "http://127.0.0.1:8083"
)


class User:
    _current_user = None

    def set_current_user(self, user):
        self._current_user = user

    def get_current_user(self):
        return self._current_user

    def logout(self):
        self._current_user = None


user = User()


def login():
    print("\nPlease enter your credentials to continue:")
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    payload = {"username": username, "password": password}
    try:
        response = requests.post(f"{USERS_URL}/login", json=payload)
    except requests.exceptions.RequestException:
        print("\nError: Unable to connect to the server.")
        main()
    if response.status_code == 200:
        print("\nLogin successful!")
        user.set_current_user(username)
        show_main_menu()
    elif response.status_code == 401:
        print("\nError: Invalid username or password. Please try again.")
    elif response.status_code == 400:
        print("\nError: Username and password are required.")
    elif response.status_code == 404:
        print("\nError: No user database found. Please register first.")
    main()


def register():
    print("\nEnter new account details:\n")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    verify = getpass.getpass("Verify Password: ")
    if password == verify:
        payload = {"username": username, "password": password}
        try:
            response = requests.post(f"{USERS_URL}/register", json=payload)
        except requests.exceptions.RequestException:
            print("\nError: Unable to connect to the server.")
            main()
        if response.status_code == 201:
            print("\nAccount created successfully!")
        elif response.status_code == 409:
            print("\nError: Username already exists.")
            register()
        elif response.status_code == 400:
            print(
                "\nError: Invalid input. Please ensure all fields are filled."
            )
            register()
        user.set_current_user(username)
        show_main_menu()
    else:
        print("\nError: Passwords do not match. Please try again.")
        register()


def show_main_menu():
    print("\nMAIN MENU")
    print("\n1. Sessions\n2. Bankroll\n3. Statistics\n4. Logout\n")
    option = input("Please enter option number: ")
    while option != "1" and option != "2" and option != "3" and option != "4":
        print("\nInvalid option number. Please try again.\n")
        option = input("Please enter option number: ")
    if option == "1":
        show_sessions_menu()
    elif option == "2":
        show_bankroll_menu()
    elif option == "3":
        show_statistics_menu()
    elif option == "4":
        user.logout()
        main()


def show_statistics_menu():
    print("\nSTATISTICS MENU")
    print(
        "\n1. Get Average Length by Stakes Played\n2. Get Win Rate by "
        "Stakes Played\n3. Back to Main Menu\n"
    )
    option = input("Please enter option number: ")
    while option != "1" and option != "2" and option != "3":
        print("\nInvalid option number. Please try again.\n")
        option = input("Please enter option number: ")
    if option == "1":
        get_average_length()
    elif option == "2":
        get_winrates()
    elif option == "3":
        show_main_menu()


def get_average_length():
    username = user.get_current_user()
    url = f"{STATISTICS_URL}/get-average-lengths"
    params = {"username": username}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        average_lengths = response.json()
        print("")
        print("Average session lengths (in hours) by stake:\n")
        for stake, avg_length in average_lengths.items():
            print(f"Stake {stake}: {avg_length} hours")
    else:
        print("No sessions for you to calculate statistics")
    print("")
    show_statistics_menu()


def get_winrates():
    username = user.get_current_user()
    url = f"{STATISTICS_URL}/get-winrates"
    params = {"username": username}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        total_winrates_by_stake = response.json()
        print("")
        print("Win rate ($ / hr) by stake:\n")
        for stake, win_rate in total_winrates_by_stake.items():
            print(f"Stake {stake}: ${win_rate:.2f}/hr")
    else:
        print("No sessions for you to calculate statistics")
    print("")
    show_statistics_menu()


def view_bankroll():
    username = user.get_current_user()
    endpoint = f"{BANKROLL_URL}/get-balance"
    params = {"username": username}
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        balance = response.json()["balance"]
        print("")
        print(f"Your balance is: ${balance:,.2f}")
    else:
        print("Error fetching balance.")
    show_bankroll_menu()


def add_remove_funds():
    print("\nAdd/Remove Funds\n")
    while True:
        date_input = input("Enter Date (MM/DD/YY): ")
        try:
            valid_date = datetime.strptime(date_input, "%m/%d/%y")
            break
        except ValueError:
            print("Invalid date format. Please use MM/DD/YY.")
    while True:
        deposit_input = input("Enter deposits (positive number): ")
        try:
            deposit = float(deposit_input)
            if deposit >= 0:
                break
            else:
                print("Deposit amount must be a positive number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    while True:
        withdrawal_input = input("Enter withdrawals (positive number): ")
        try:
            withdrawals = float(withdrawal_input)
            if withdrawals >= 0:
                break
            else:
                print("Withdrawal amount must be a positive number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    net = deposit - withdrawals
    print("\nYou have entered:\n")
    print(f"Date: {valid_date.strftime('%m/%d/%y')}")
    print(f"Deposits: ${deposit:.2f}")
    print(f"Withdrawals: ${withdrawals:.2f}")
    print(f"Net: ${net:.2f}")
    correct = input("\nIs this correct? (y/n) ").lower()
    while correct != "y" and correct != "n":
        print("\nInvalid response. Please try again.")
        correct = input("\nIs this correct? (y/n) ").lower()
    if correct == "y":
        transaction_data = {
            "username": user.get_current_user(),
            "date": valid_date.strftime("%m/%d/%y"),
            "deposits": deposit,
            "withdrawals": withdrawals,
        }
        response = requests.post(
            BANKROLL_URL + "/post-transcation", json=transaction_data
        )
        if response.status_code == 200:
            print("Transaction processed successfully!")
            print(f"Updated Balance: ${response.json()['new_balance']:.2f}")
        else:
            print(
                f"Unexpected response: {response.status_code}, {response.text}"
            )
    elif correct == "n":
        add_remove_funds()
    again = input(
        "\nWould you like to enter another transaction? (y/n) "
    ).lower()
    while again != "y" and again != "n":
        print("\nInvalid response. Please try again.")
        again = input(
            "\nWould you like to enter another transaction? (y/n) "
        ).lower()
    if again == "y":
        add_remove_funds()
    elif again == "n":
        show_bankroll_menu()


def view_transaction_history():
    def paginate_results(data, page_size=3):
        for i in range(0, len(data), page_size):
            yield data[i : i + page_size]  # noqa: E203

    print("\nView Transactions")
    print("\nEnter date range (or leave blank for all transcations):")
    while True:
        start_date = input("Start Date (MM/DD/YY): ").strip()
        if start_date == "":
            break
        try:
            start_date = datetime.strptime(start_date, "%m/%d/%y")
            print(
                "You have entered a start date. Please also enter an end date."
            )
            end_date = input("End Date (MM/DD/YY): ").strip()
            end_date = datetime.strptime(end_date, "%m/%d/%y")
            break
        except ValueError:
            print("Invalid date format. Please use MM/DD/YY.")

    if start_date == "":
        print("")
        params = {"username": user.get_current_user()}
        response = requests.get(
            BANKROLL_URL + "/get-transcations", params=params
        )
        stop = False
        if response.status_code == 200:
            transactions = response.json()
            paginator = paginate_results(transactions, page_size=3)
            for page in paginator:
                if stop:
                    break
                print(json.dumps(page, indent=4))
                print("")
                print("")
                print(
                    "...Press Enter to continue to the next page, or type"
                    "'quit' to stop...."
                )
                user_input = input()
                if user_input == "quit":
                    stop = True
        elif response.status_code == 404:
            print("No transcations have been recorded for you.")
        show_bankroll_menu()
    else:
        print("")
        params = {
            "username": user.get_current_user(),
            "start_date": start_date.strftime("%m/%d/%y"),
            "end_date": end_date.strftime("%m/%d/%y"),
        }
        response = requests.get(
            BANKROLL_URL + "/get-transactions", params=params
        )
        stop = False
        if response.status_code == 200:
            transactions = response.json()
            paginator = paginate_results(transactions, page_size=3)
            for page in paginator:
                if stop:
                    break
                print(json.dumps(page, indent=4))
                print("")
                print("")
                print(
                    "...Press Enter to continue to the next page, or type "
                    "'quit' to stop...."
                )
                user_input = input()
                if user_input == "quit":
                    stop = True
        elif response.status_code == 404:
            print(
                "No transcations have been recorded for "
                "you in this date range."
            )
        show_bankroll_menu()


def reset_bankroll_data():
    print("\nReset Bankroll Data")
    print("\nWARNING: Selecting this option erases all bankroll data.")
    confirm = input("\nAre you sure you want to do this? (y/n) ").lower()
    while confirm != "y" and confirm != "n":
        print("\nInvalid input. Please try again.\n")
        confirm = input("\nAre you sure you want to do this? (y/n) ").lower()
    if confirm == "y":
        params = {"username": user.get_current_user()}
        response = requests.delete(
            BANKROLL_URL + "/delete-finances", params=params
        )
        if response.status_code == 200:
            print("\nAll bankroll data deleted.")
        else:
            print(f"Error: {response.json()['error']}")
    show_bankroll_menu()


def show_bankroll_menu():
    print("\nBANKROLL MENU")
    print(
        "\n1. View Bankroll\n2. Add/Remove Funds\n3. View Transaction History"
        "\n4. Reset Bankroll Data\n5. Back to Main Menu\n"
    )
    option = input("Please enter option number: ")
    while (
        option != "1"
        and option != "2"
        and option != "3"
        and option != "4"
        and option != "5"
    ):
        print("\nInvalid option number. Please try again.\n")
        option = input("Please enter option number: ")
    if option == "1":
        view_bankroll()
    elif option == "2":
        add_remove_funds()
    elif option == "3":
        view_transaction_history()
    elif option == "4":
        reset_bankroll_data()
    elif option == "5":
        show_main_menu()


def enter_session(is_detailed):
    print("")
    while True:
        date_input = input("Enter Date (MM/DD/YY): ")
        try:
            valid_date = datetime.strptime(date_input, "%m/%d/%y")
            break
        except ValueError:
            print("Invalid date format. Please use MM/DD/YY.")

    length_input = input("Enter session length (in minutes): ")
    stakes_input = input("Enter stakes (e.g., 1/2): ")
    buyin_input = input("Enter buy-in amount: ")
    cashout_input = input("Enter cash-out amount: ")
    if is_detailed:
        location_input = input("Enter Location: ")
        table_notes = input("Enter Table Notes: ")
        notable_hands = input("Enter Notable Hands: ")

    print("\nYou have entered:")
    print(f"\nDate: {valid_date.strftime('%m/%d/%y')}")
    print(f"Length: {length_input} minutes")
    print(f"Stakes: {stakes_input}")
    print(f"Buyin: ${buyin_input}")
    print(f"Cashout: ${cashout_input}")
    if is_detailed:
        print(f"Location: ${location_input}")
        print(f"Table Notes: ${table_notes}")
        print(f"Notable Hands: ${notable_hands}")

    correct = input("\nIs this correct? (y/n) ").lower()
    while correct != "y" and correct != "n":
        print("\nInvalid response. Please try again.")
        correct = input("\nIs this correct? (y/n) ").lower()
    if correct == "y":
        session_data = {
            "username": user.get_current_user(),
            "date": valid_date.strftime("%m/%d/%y"),
            "length": int(length_input),
            "stakes": stakes_input,
            "buyin": float(buyin_input),
            "cashout": float(cashout_input),
            "location": location_input if is_detailed else "",
            "notes": table_notes if is_detailed else "",
            "notable_hands": notable_hands if is_detailed else "",
        }
        response = requests.post(
            SESSIONS_URL + "/add-session", json=session_data
        )
        if response.status_code == 201:
            print("\nSession recorded successfully!")
        else:
            print(
                "\nFailed to record session. Error:",
                response.json().get("error", "Unknown error"),
            )
    elif correct == "n":
        enter_session(is_detailed)

    again = input("\nWould you like to enter another session? (y/n) ").lower()
    while again != "y" and again != "n":
        print("\nInvalid response. Please try again.")
        again = input(
            "\nWould you like to enter another session? (y/n) "
        ).lower()
    if again == "y":
        enter_session(is_detailed)
    elif again == "n":
        show_sessions_menu()


def start_new_session_menu():
    print("\nSTART NEW SESSION")
    print("\n1. Basic\n2. Detailed\n3. Back to Sessions Menu\n")
    option = input("Please enter option number: ")
    while option != "1" and option != "2" and option != "3":
        print("\nInvalid option number. Please try again.\n")
        option = input("Please enter option number: ")
    if option == "1":
        enter_session(False)
    elif option == "2":
        enter_session(True)
    elif option == "3":
        show_sessions_menu()


def view_session_history_menu():
    def paginate_results(data, page_size=3):
        for i in range(0, len(data), page_size):
            yield data[i : i + page_size]  # noqa: E203

    print("\nView Sessions")
    print("\nEnter date range (or leave blank for all sessions):")
    while True:
        start_date = input("Start Date (MM/DD/YY): ").strip()
        if start_date == "":
            break
        try:
            start_date = datetime.strptime(start_date, "%m/%d/%y")
            print(
                "You have entered a start date. Please also enter an end date."
            )
            end_date = input("End Date (MM/DD/YY): ").strip()
            end_date = datetime.strptime(end_date, "%m/%d/%y")
            break
        except ValueError:
            print("Invalid date format. Please use MM/DD/YY.")

    if start_date == "":
        print("")
        params = {"username": user.get_current_user()}
        response = requests.get(SESSIONS_URL + "/get-sessions", params=params)
        stop = False
        if response.status_code == 200:
            sessions = response.json()
            paginator = paginate_results(sessions, page_size=3)
            for page in paginator:
                if stop:
                    break
                print(json.dumps(page, indent=4))
                print("")
                print("")
                print(
                    "...Press Enter to continue to the next page, or type"
                    "'quit' to stop...."
                )
                user_input = input()
                if user_input == "quit":
                    stop = True
        elif response.status_code == 404:
            print("No sessions have been recorded for you.")
        show_sessions_menu()
    else:
        print("")
        params = {
            "username": user.get_current_user(),
            "start_date": start_date.strftime("%m/%d/%y"),
            "end_date": end_date.strftime("%m/%d/%y"),
        }
        response = requests.get(SESSIONS_URL + "/get-sessions", params=params)
        stop = False
        if response.status_code == 200:
            sessions = response.json()
            paginator = paginate_results(sessions, page_size=3)
            for page in paginator:
                if stop:
                    break
                print(json.dumps(page, indent=4))
                print("")
                print("")
                print(
                    "...Press Enter to continue to the next page, or type "
                    "'quit' to stop...."
                )
                user_input = input()
                if user_input == "quit":
                    stop = True
        elif response.status_code == 404:
            print("No sessions have been recorded for you.")
        show_sessions_menu()


def reset_sessions():
    print("\nReset Session Data")
    print("\nWARNING: Selecting this option erases all session data.")
    confirm = input("\nAre you sure you want to do this? (y/n) ").lower()
    while confirm != "y" and confirm != "n":
        print("\nInvalid input. Please try again.\n")
        confirm = input("\nAre you sure you want to do this? (y/n) ").lower()
    if confirm == "y":
        params = {"username": user.get_current_user()}
        response = requests.delete(
            SESSIONS_URL + "/delete-sessions", params=params
        )
        if response.status_code == 200:
            print("\nAll session data deleted.")
        else:
            print(f"Error: {response.json()['error']}")
    show_sessions_menu()


def show_sessions_menu():
    print("\nSESSIONS MENU")
    print(
        "\n1. Start New Session\n2. View Session History\n3. Reset Sessions "
        "Data\n4. Back to Main Menu\n"
    )
    option = input("Please enter option number: ")
    while option != "1" and option != "2" and option != "3" and option != "4":
        print("\nInvalid option number. Please try again.\n")
        option = input("Please enter option number: ")
    if option == "1":
        start_new_session_menu()
    elif option == "2":
        view_session_history_menu()
    elif option == "3":
        reset_sessions()
    elif option == "4":
        show_main_menu()


def show_welcome_screen():
    with open("welcome_art.txt") as f:
        print(f.read())
    print("Welcome to Poker Tracker!")
    print("\nImportant messages for users:")
    print(
        "- Tracking your poker play helps you identify patterns and improve "
        "your strategy over time."
    )
    print(
        "- Accurately and meticulously logging your poker sessions and "
        "bankroll requires additional time but will provide more accurate "
        "post-session analysis."
    )
    print("\n1. Login\n2. Create Account\n3. Exit\n")


def exit_program():
    sys.exit()


def main():
    show_welcome_screen()
    option = input("Please enter option number: ")
    while option != "1" and option != "2" and option != "3":
        print("\nInvalid option number. Please try again.\n")
        option = input("Please enter option number: ")
    if option == "1":
        login()
    elif option == "2":
        register()
    elif option == "3":
        exit_program()


if __name__ == "__main__":
    main()
