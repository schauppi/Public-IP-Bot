# Public IP Tracker Bot

This Telegram bot helps users identify their public IP address and tracks changes when they do not have a static IP. It polls for IP changes every X minutes, providing notifications if any change occurs.

## Features

- **IP Identification**: Quickly fetches and displays your current public IP address.
- **Continuous Monitoring**: Polls for IP changes every X minutes and notifies you of any changes.
- **Customizable Polling Interval**: Allows setting of custom polling intervals.
- **Commands**:
  - `/ip`: Returns your current public IP address.
  - `/start_poll_ip`: Starts the IP address monitoring.
  - `/stop_poll_ip`: Stops the IP address monitoring.
  - `/set_poll`: Sets the polling interval in seconds.
  - `/status`: Displays the current status of IP monitoring and the polling interval.

## Prerequisites

Before you can use this bot, you need:
- Python 3.8 or higher
- `pip` for installing dependencies

## Installation

1. **Clone the Repository**:
   - `git clone https://github.com/schauppi/Public-IP-Bot.git`
   - `cd Public-IP-Bot`

2. **Install Dependencies**:
    - `pip install -r requirements.txt`

3. **Create a Telegram Bot**:
    - Talk to the [BotFather](https://core.telegram.org/bots#botfather) on Telegram to create a new bot and get the API token.

4. **Configuration**:
    - Rename the `.env.example` file to `.env`.
    - Add the API token from the BotFather to the `.env` file.

5. **Run the Bot**:
    - `python main.py`