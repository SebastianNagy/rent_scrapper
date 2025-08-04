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

## Important information
Funda (out of the websites I've tested) requires an initial 'human verification'. Once the funda web page loads for the first time you need to manually go through the human verification so that the scrapper actually works for Funda. Otherwise, it's going to be permanently stuck and not scrap anything. Once the verification is passed, the current scrapping 'session' will work for Funda.