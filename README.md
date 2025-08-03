# Rent Scrapper
NL Rent Scrapper with a Telegram bot to notify new listings

## .env file
Create a file called `.env` with the following two entries:
```
BOT_TOKEN=<YOUR TELEGRAM BOT TOKEN>
CHAT_ID=<YOUR TELEGRAM CHAT ID>
```

## How to use?
Modify the `rental_scrapper.py` script by adding your own URLs and HTML/regex parsers to extract the value from the website you're interested in, and add them to the main loop also.


Funda, Rentola, Pararius and Verra already have working parsers, you just need to add URLs with your own preferences.