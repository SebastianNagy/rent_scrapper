import re
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime

import telegram_bot
from utils import log, CHECK_INTERVAL_S


# Set up Selenium to use a Chrome browser
browser_options = webdriver.ChromeOptions()
# browser_options.add_argument("--user-data-dir=/home/sebastian/wa_rent/user_data_dir")
# browser_options.add_argument('--profile-directory=Default')  # Use the Guest Profile to avoid login issues
# browser_options.add_argument("--headless")  # Run in headless mode for faster performance


class Scrapper:
    def __init__(self, shared_status, ID, URL, findall_kwargs, extra_regex=None):
        self.browser = None
        self.shared_status = shared_status
        self.ID = ID
        self.URL = URL
        self.findall_kwargs = findall_kwargs
        self.extra_regex = extra_regex
        self.last_known_count = None
        self.last_succesful_count_dt = None

        # Initialize the status in the shared dictionary
        self.shared_status[self.ID] = {
            'status': 'initializing',
            'count': None,
            'last_update': None
        }

    def get_rental_count(self):
        """Scrapes the URL and returns the number of rental listings."""
        try:
            self.browser.get(self.URL)
            time.sleep(5)  # Allow time for JavaScript to load content

            html_content = self.browser.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            count_element = soup.find_all(**self.findall_kwargs)

            if count_element:
                if self.extra_regex is not None:
                    count_element = [int(x) for x in re.findall(self.extra_regex, count_element[0])]
                count_text = re.findall(r"(\d+)", str(count_element[0]))[0]

                self.last_succesful_count_dt = datetime.now()
                return int(count_text)
            else:
                return None

        except requests.exceptions.RequestException as e:
            log(f"Error during request: {e}")
            return None
        except Exception as e:
            log(f"An unexpected error occurred: {e}")
            return None

    def scrapper_loop(self):
        self.browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=browser_options)
        """Main loop to check for updates and send notifications."""
        log(f"Starting {self.ID} rental scraper...")

        while self.last_known_count is None:
            self.last_known_count = self.get_rental_count()

            if self.last_known_count is not None:
                log(f"[{self.ID}] Initial rental count is: {self.last_known_count}")
                # Update shared status
                self.shared_status[self.ID] = {
                    'status': 'running',
                    'count': self.last_known_count,
                    'last_update': datetime.now()
                }
                telegram_bot.send_telegram_message(f"🔎 *{self.ID}* Scraper started. Initial rental count is {self.last_known_count}.", markdown=True)
            else:
                log(f"[{self.ID}] Could not fetch initial count. Will retry in 20s...")
                time.sleep(20)

        while True:
            try:
                # Wait for the specified interval before checking again
                time.sleep(CHECK_INTERVAL_S + random.randint(-10, 10))

                log(f"[{self.ID}] Checking for new rental listings...")
                current_count = self.get_rental_count()

                if current_count is not None:
                    log(f"[{self.ID}] Current count is: {current_count}. Last known count was: {self.last_known_count}")
                    # Check if the count has changed since the last check
                    if self.last_known_count is not None and current_count != self.last_known_count:
                        log(f"[{self.ID}] Rental count changed! From {self.last_known_count} to {current_count}. Sending notification...")

                        # Create a helpful message
                        change = "increased" if current_count > self.last_known_count else "decreased"
                        message = f"📢 {self.ID} Alert! \n\n" +\
                            f"The number of rentals has *{change}* from {self.last_known_count} to {current_count}.\n\n" +\
                            f"Check them out here: {URL}"

                        telegram_bot.send_telegram_message(message)
                        self.last_known_count = current_count
                    elif self.last_known_count is None:
                        # If the first check failed but this one succeeded
                        self.last_known_count = current_count
                        telegram_bot.send_telegram_message(f"✅ *{self.ID}* Scraper successfully fetched data. Current count is {current_count}.", markdown=True)

                    # Always update the shared status with the latest info
                    self.shared_status[self.ID] = {
                        'status': 'running',
                        'count': self.last_known_count,
                        'last_update': datetime.now()
                    }
            except KeyboardInterrupt:
                log(f"[{self.ID}] Scraper stopped by user.")
                break
            except Exception as e:
                log(f"An error occurred in the main loop: {e}")
                # Report crash to shared dictionary
                self.shared_status[self.ID] = {
                    'status': 'crashed',
                    'error': str(e),
                    'last_update': datetime.now(),
                    'count': self.last_known_count,
                }
                telegram_bot.send_telegram_message(f"❌ *{ID}* Scraper crashed: {e}", markdown=True)

        self.browser.quit()  # Close the browser when done
        self.browser = None
        self.last_known_count = None
        log(f"[{self.ID}] Scraper has stopped.")
    
    def get_status_update(self):
        """Returns the current status of the scraper."""
        if self.last_succesful_count_dt is None:
            return f"❗{self.ID} Scraper has not yet fetched any data."
        
        time_since_last_update = datetime.now() - self.last_succesful_count_dt
        return f"🔃{self.ID} Scraper last updated {time_since_last_update.total_seconds()} seconds ago. Current count: {self.last_known_count}"