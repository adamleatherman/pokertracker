# PokerTracker

PokerTracker is a command-line application for managing your poker sessions, bankroll, and analyzing your performance. It helps players track session data, manage finances, and view key statistics over time.

## Features

- **User Management**: Register, log in, and manage user sessions.
- **Session Management**: Record poker sessions with details like date, length, stakes, buy-in, cash-out, location, and notes.
- **Bankroll Management**: Track deposits and withdrawals, with automatic balance calculations.
- **Statistics**: View stats like average session length, win rate (dollars per hour), and more.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/adamleatherman/pokertracker
   cd PokerTracker
   ```
2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Start all services:
    ```bash
    python users_service.py
    python statistics_service.py
    python bankroll_service.py
    python sessions_service.py
    ```
4. Start main program:
    ```bash
    python main.py
    ```