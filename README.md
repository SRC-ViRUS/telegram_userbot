# Telegram Userbot

## Installation

Create a virtual environment if desired and install the required packages:

```bash
pip install -r requirements.txt
# You also need ffmpeg installed and available in your PATH
# For Debian/Ubuntu you can run:
sudo apt-get install ffmpeg
```

## Configuration

Edit `config.py` and set the following values with your Telegram credentials:

```python
API_ID = 123456
API_HASH = "your_api_hash"
SESSION_STRING = "your_session_string"
```

You can obtain the API information from <https://my.telegram.org>. The `SESSION_STRING` can be generated with tools such as Telethon or Pyrogram.

## Running

After installing the dependencies and configuring `config.py`, start the bot with:

```bash
python main.py
```

## Commands

For a detailed list of available commands, see [COMMANDS.md](COMMANDS.md).
