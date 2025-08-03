
import os
import re
import time
import random
import requests
from multiprocessing import Process
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from datetime import datetime


# --- CONFIGURATION ---
load_dotenv()  # Load environment variables from .env file
CHECK_INTERVAL = 30  # 30 seconds
TELEGRAM_BOT_TOKEN = os.getenv('BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')
# --- CONFIGURATION ---

# The URLs to scrape
FUNDA_URL = 'https://www.funda.nl/en/zoeken/huur?selected_area=[%22delft%22,%22rijswijk-zh%22,%22den-haag%22,%22den-hoorn-zh%22]&price=%220-1750%22&object_type=[%22apartment%22,%22house%22]&floor_area=%2250-%22&sort=%22date_down%22'
RENTOLA_URL = 'https://rentola.nl/en/rent?location=delft&order=desc&rent=0-1750&size=49'
PARARIUS_DELFT_URL = 'https://www.pararius.com/apartments/delft/0-1750/radius-5/50m2'
PARARIUS_RIJSWIJK_URL = 'https://www.pararius.com/apartments/rijswijk/0-1750/radius-5/50m2'
VERRA_DELFT_URL = 'https://www.verra.nl/en/listings/rental?salesRentals=rentals#{%22view%22:%22grid%22,%22sort%22:%22addedDesc%22,%22searchTerms%22:[%22address%22,%22zipcode%22,%22city%22,%22state%22],%22address%22:%22%22,%22title%22:%22%22,%22salesRentals%22:%22rentals%22,%22salesPriceMin%22:0,%22salesPriceMax%22:9999999999,%22devSalesPriceMin%22:0,%22devSalesPriceMax%22:9999999999,%22rentalsPriceMin%22:0,%22rentalsPriceMax%22:2000,%22devRentalsPriceMin%22:0,%22devRentalsPriceMax%22:9999999999,%22surfaceMin%22:50,%22surfaceMax%22:9999999999,%22unitsMin%22:0,%22unitsMax%22:9999999999,%22devSurfaceMin%22:0,%22devSurfaceMax%22:9999999999,%22plotSurfaceMin%22:0,%22plotSurfaceMax%22:9999999999,%22roomsMin%22:0,%22roomsMax%22:9999999999,%22bedroomsMin%22:0,%22bedroomsMax%22:9999999999,%22bathroomsMin%22:0,%22bathroomsMax%22:9999999999,%22city%22:[%22Delft%22],%22district%22:[],%22mainType%22:[],%22buildType%22:[],%22tag%22:[],%22country%22:[],%22state%22:[],%22listingsType%22:[],%22ignoreType%22:[],%22categories%22:[],%22status%22:%22all%22,%22statusStrict%22:true,%22includeIsBought%22:false,%22user%22:%22%22,%22branch%22:%22%22,%22apartmentType%22:%22%22,%22houseType%22:%22%22,%22archiveTime%22:86400,%22page%22:1,%22grouped%22:true}'
VERRA_RIJSWIJK_URL = 'https://www.verra.nl/en/listings/rental?salesRentals=rentals#{%22view%22:%22grid%22,%22sort%22:%22addedDesc%22,%22searchTerms%22:[%22address%22,%22zipcode%22,%22city%22,%22state%22],%22address%22:%22%22,%22title%22:%22%22,%22salesRentals%22:%22rentals%22,%22salesPriceMin%22:0,%22salesPriceMax%22:9999999999,%22devSalesPriceMin%22:0,%22devSalesPriceMax%22:9999999999,%22rentalsPriceMin%22:0,%22rentalsPriceMax%22:2000,%22devRentalsPriceMin%22:0,%22devRentalsPriceMax%22:9999999999,%22surfaceMin%22:50,%22surfaceMax%22:9999999999,%22unitsMin%22:0,%22unitsMax%22:9999999999,%22devSurfaceMin%22:0,%22devSurfaceMax%22:9999999999,%22plotSurfaceMin%22:0,%22plotSurfaceMax%22:9999999999,%22roomsMin%22:0,%22roomsMax%22:9999999999,%22bedroomsMin%22:0,%22bedroomsMax%22:9999999999,%22bathroomsMin%22:0,%22bathroomsMax%22:9999999999,%22city%22:[%22Rijswijk%22],%22district%22:[],%22mainType%22:[],%22buildType%22:[],%22tag%22:[],%22country%22:[],%22state%22:[],%22listingsType%22:[],%22ignoreType%22:[],%22categories%22:[],%22status%22:%22all%22,%22statusStrict%22:true,%22includeIsBought%22:false,%22user%22:%22%22,%22branch%22:%22%22,%22apartmentType%22:%22%22,%22houseType%22:%22%22,%22archiveTime%22:86400,%22page%22:1,%22grouped%22:true}'
VERRA_HAGUE_URL = 'https://www.verra.nl/en/listings/rental?salesRentals=rentals#{%22view%22:%22grid%22,%22sort%22:%22addedDesc%22,%22searchTerms%22:[%22address%22,%22zipcode%22,%22city%22,%22state%22],%22address%22:%22%22,%22title%22:%22%22,%22salesRentals%22:%22rentals%22,%22salesPriceMin%22:0,%22salesPriceMax%22:9999999999,%22devSalesPriceMin%22:0,%22devSalesPriceMax%22:9999999999,%22rentalsPriceMin%22:0,%22rentalsPriceMax%22:2000,%22devRentalsPriceMin%22:0,%22devRentalsPriceMax%22:9999999999,%22surfaceMin%22:50,%22surfaceMax%22:9999999999,%22unitsMin%22:0,%22unitsMax%22:9999999999,%22devSurfaceMin%22:0,%22devSurfaceMax%22:9999999999,%22plotSurfaceMin%22:0,%22plotSurfaceMax%22:9999999999,%22roomsMin%22:0,%22roomsMax%22:9999999999,%22bedroomsMin%22:0,%22bedroomsMax%22:9999999999,%22bathroomsMin%22:0,%22bathroomsMax%22:9999999999,%22city%22:[%22Den%20Haag%22],%22district%22:[],%22mainType%22:[],%22buildType%22:[],%22tag%22:[],%22country%22:[],%22state%22:[],%22listingsType%22:[],%22ignoreType%22:[],%22categories%22:[],%22status%22:%22all%22,%22statusStrict%22:true,%22includeIsBought%22:false,%22user%22:%22%22,%22branch%22:%22%22,%22apartmentType%22:%22%22,%22houseType%22:%22%22,%22archiveTime%22:86400,%22page%22:1,%22grouped%22:true}'

# The findall_kwargs for each URL to extract the rental count
VERRA_KWARGS = {'name': 'span', 'attrs': {'class': 'realtime-listings-total'}}
RENTOLA_KWARGS = {'string': re.compile(r"(\d+)\s+properties found", re.IGNORECASE)}
FUNDA_KWARGS = {'string': re.compile(r"(\d+)\s+homes for rent", re.IGNORECASE)}
PARARIUS_KWARGS = {'string': re.compile(r"with\s+(\d+)\s+properties\s+for\s+rent", re.IGNORECASE)}

# Extra regex for filtering
PARARIUS_EXTRA_REGEX = re.compile(r"with\s+(\d+)\s+properties\s+for\s+rent", re.IGNORECASE)

# Set up Selenium to use a Chrome browser
browser_options = webdriver.ChromeOptions()
# browser_options.add_argument("--user-data-dir=/home/sebastian/wa_rent/user_data_dir")
# browser_options.add_argument('--profile-directory=Default')  # Use the Guest Profile to avoid login issues
# browser_options.add_argument("--headless")  # Run in headless mode for faster performance


def log(message):
    """Logs messages with a timestamp."""
    print(f"[{datetime.now()}] {message}")


def get_rental_count(browser, URL, findall_kwargs, extra_regex=None):
    """Scrapes the URL and returns the number of rental listings."""
    try:
        browser.get(URL)
        # log(f"Fetching URL with Selenium: {browser.current_url}")

        # Give the page a few seconds to load all JavaScript content
        time.sleep(5)

        # Get the page source after JavaScript has run
        html_content = browser.page_source

        soup = BeautifulSoup(html_content, 'html.parser')
        count_element = soup.find_all(**findall_kwargs)
        

        if count_element:
            # Get the first number appearance in the text of the found HTML element
            if extra_regex is not None:
                count_element = [int(x) for x in re.findall(extra_regex, count_element[0])]
            count_text = re.findall(r"(\d+)", str(count_element[0]))[0]
            return int(count_text)
        else:
            # log("Could not find the rental count element on the page!")
            return None

    except requests.exceptions.RequestException as e:
        log(f"Error during request: {e}")
        return None
    except Exception as e:
        log(f"An unexpected error occurred: {e}")
        return None


def send_telegram_message(message):
    """Sends a message to the specified Telegram chat using the bot."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log("Telegram token or chat ID is not set. Cannot send message.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        # 'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            log(f"Failed to send Telegram message. Status code: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
            # ("VERRA RIJSWIJK", VERRA_RIJSWIJK_URL, VERRA_KWARGS),
            # ("VERRAtion as e:
        log(f"Error sending Telegram message: {e}")


def scrapper_loop(ID, URL, findall_kwargs, extra_regex=None):
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=browser_options)
    """Main loop to check for updates and send notifications."""
    log(f"Starting {ID} rental scraper...")

    last_known_count = None
    while last_known_count is None:
        last_known_count = get_rental_count(browser, URL, findall_kwargs=findall_kwargs, extra_regex=extra_regex)

        if last_known_count is not None:
            log(f"[{ID}] Initial rental count is: {last_known_count}")
            send_telegram_message(f"🔎 {ID} Scraper started. Initial rental count is {last_known_count}.")
        else:
            log(f"[{ID}] Could not fetch initial count. Will retry in 20s...")
            time.sleep(20)

    while True:
        try:
            # Wait for the specified interval before checking again
            time.sleep(CHECK_INTERVAL + random.randint(-10, 10))

            log(f"[{ID}] Checking for new rental listings...")
            current_count = get_rental_count(browser, URL, findall_kwargs=findall_kwargs, extra_regex=extra_regex)

            if current_count is not None:
                log(f"[{ID}] Current count is: {current_count}. Last known count was: {last_known_count}")
                # Check if the count has changed since the last check
                if last_known_count is not None and current_count != last_known_count:
                    log(f"[{ID}] Rental count changed! From {last_known_count} to {current_count}. Sending notification...")

                    # Create a helpful message
                    change = "increased" if current_count > last_known_count else "decreased"
                    message = f"📢 {ID} Alert! \n\n" +\
                        f"The number of rentals has *{change}* from {last_known_count} to {current_count}.\n\n" +\
                        f"Check them out here: {URL}"

                    send_telegram_message(message)
                    last_known_count = current_count
                elif last_known_count is None:
                    # If the first check failed but this one succeeded
                    last_known_count = current_count
                    send_telegram_message(f"✅ {ID} Scraper successfully fetched data. Current count is {current_count}.")
                else:
                    log(f"[{ID}] No change in rental count.")

        except KeyboardInterrupt:
            log(f"[{ID}] Scraper stopped by user.")
            break
        except Exception as e:
            log(f"An error occurred in the main loop: {e}")
            send_telegram_message(f"❌ {ID} Scraper crashed: {e}")

    browser.quit()  # Close the browser when done


if __name__ == "__main__":

    processes = []
    for args in [
            ("FUNDA", FUNDA_URL, FUNDA_KWARGS),
            ("PARARIUS DELFT", PARARIUS_DELFT_URL, PARARIUS_KWARGS, PARARIUS_EXTRA_REGEX),
            ("PARARIUS RIJSWIJK", PARARIUS_RIJSWIJK_URL, PARARIUS_KWARGS, PARARIUS_EXTRA_REGEX),
            ("VERRA DELFT", VERRA_DELFT_URL, VERRA_KWARGS),
            ("VERRA RIJSWIJK", VERRA_RIJSWIJK_URL, VERRA_KWARGS),
            ("VERRA HAGUE", VERRA_HAGUE_URL, VERRA_KWARGS)
    ]:

        process = Process(target=scrapper_loop, args=args)
        process.start()
        processes.append(process)
        time.sleep(1)

    for process in processes:
        process.join()
