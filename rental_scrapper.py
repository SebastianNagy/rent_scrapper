import re
import time
import multiprocessing as mp

import telegram_bot
from scrapper import Scrapper
from utils import log


# The URLs to scrape
FUNDA_URL = 'https://www.funda.nl/en/zoeken/huur?selected_area=[%22delft%22,%22rijswijk-zh%22,%22den-haag%22,%22den-hoorn-zh%22]&price=%220-1750%22&object_type=[%22apartment%22,%22house%22]&floor_area=%2250-%22&sort=%22date_down%22'
RENTOLA_DELFT_URL = 'https://rentola.nl/en/rent?location=delft&order=desc&rent=0-1750&size=49'
RENTOLA_RIJSWIJK_URL = 'https://rentola.nl/en/rent?location=rijswijk&order=desc&rent=0-1750&size=49'
PARARIUS_DELFT_URL = 'https://www.pararius.com/apartments/delft/0-1750/radius-5/50m2'
PARARIUS_RIJSWIJK_URL = 'https://www.pararius.com/apartments/rijswijk/0-1750/radius-5/50m2'
VERRA_DELFT_URL = 'https://www.verra.nl/en/listings/rental?salesRentals=rentals#{%22view%22:%22grid%22,%22sort%22:%22addedDesc%22,%22searchTerms%22:[%22address%22,%22zipcode%22,%22city%22,%22state%22],%22address%22:%22%22,%22title%22:%22%22,%22salesRentals%22:%22rentals%22,%22salesPriceMin%22:0,%22salesPriceMax%22:9999999999,%22devSalesPriceMin%22:0,%22devSalesPriceMax%22:9999999999,%22rentalsPriceMin%22:0,%22rentalsPriceMax%22:2000,%22devRentalsPriceMin%22:0,%22devRentalsPriceMax%22:9999999999,%22surfaceMin%22:50,%22surfaceMax%22:9999999999,%22unitsMin%22:0,%22unitsMax%22:9999999999,%22devSurfaceMin%22:0,%22devSurfaceMax%22:9999999999,%22plotSurfaceMin%22:0,%22plotSurfaceMax%22:9999999999,%22roomsMin%22:0,%22roomsMax%22:9999999999,%22bedroomsMin%22:0,%22bedroomsMax%22:9999999999,%22bathroomsMin%22:0,%22bathroomsMax%22:9999999999,%22city%22:[%22Delft%22],%22district%22:[],%22mainType%22:[],%22buildType%22:[],%22tag%22:[],%22country%22:[],%22state%22:[],%22listingsType%22:[],%22ignoreType%22:[],%22categories%22:[],%22status%22:%22all%22,%22statusStrict%22:true,%22includeIsBought%22:false,%22user%22:%22%22,%22branch%22:%22%22,%22apartmentType%22:%22%22,%22houseType%22:%22%22,%22archiveTime%22:86400,%22page%22:1,%22grouped%22:true}'
VERRA_RIJSWIJK_URL = 'https://www.verra.nl/en/listings/rental?salesRentals=rentals#{%22view%22:%22grid%22,%22sort%22:%22addedDesc%22,%22searchTerms%22:[%22address%22,%22zipcode%22,%22city%22,%22state%22],%22address%22:%22%22,%22title%22:%22%22,%22salesRentals%22:%22rentals%22,%22salesPriceMin%22:0,%22salesPriceMax%22:9999999999,%22devSalesPriceMin%22:0,%22devSalesPriceMax%22:9999999999,%22rentalsPriceMin%22:0,%22rentalsPriceMax%22:2000,%22devRentalsPriceMin%22:0,%22devRentalsPriceMax%22:9999999999,%22surfaceMin%22:50,%22surfaceMax%22:9999999999,%22unitsMin%22:0,%22unitsMax%22:9999999999,%22devSurfaceMin%22:0,%22devSurfaceMax%22:9999999999,%22plotSurfaceMin%22:0,%22plotSurfaceMax%22:9999999999,%22roomsMin%22:0,%22roomsMax%22:9999999999,%22bedroomsMin%22:0,%22bedroomsMax%22:9999999999,%22bathroomsMin%22:0,%22bathroomsMax%22:9999999999,%22city%22:[%22Rijswijk%22],%22district%22:[],%22mainType%22:[],%22buildType%22:[],%22tag%22:[],%22country%22:[],%22state%22:[],%22listingsType%22:[],%22ignoreType%22:[],%22categories%22:[],%22status%22:%22all%22,%22statusStrict%22:true,%22includeIsBought%22:false,%22user%22:%22%22,%22branch%22:%22%22,%22apartmentType%22:%22%22,%22houseType%22:%22%22,%22archiveTime%22:86400,%22page%22:1,%22grouped%22:true}'
VERRA_HAGUE_URL = 'https://www.verra.nl/en/listings/rental?salesRentals=rentals#{%22view%22:%22grid%22,%22sort%22:%22addedDesc%22,%22searchTerms%22:[%22address%22,%22zipcode%22,%22city%22,%22state%22],%22address%22:%22%22,%22title%22:%22%22,%22salesRentals%22:%22rentals%22,%22salesPriceMin%22:0,%22salesPriceMax%22:9999999999,%22devSalesPriceMin%22:0,%22devSalesPriceMax%22:9999999999,%22rentalsPriceMin%22:0,%22rentalsPriceMax%22:2000,%22devRentalsPriceMin%22:0,%22devRentalsPriceMax%22:9999999999,%22surfaceMin%22:50,%22surfaceMax%22:9999999999,%22unitsMin%22:0,%22unitsMax%22:9999999999,%22devSurfaceMin%22:0,%22devSurfaceMax%22:9999999999,%22plotSurfaceMin%22:0,%22plotSurfaceMax%22:9999999999,%22roomsMin%22:0,%22roomsMax%22:9999999999,%22bedroomsMin%22:0,%22bedroomsMax%22:9999999999,%22bathroomsMin%22:0,%22bathroomsMax%22:9999999999,%22city%22:[%22Den%20Haag%22],%22district%22:[],%22mainType%22:[],%22buildType%22:[],%22tag%22:[],%22country%22:[],%22state%22:[],%22listingsType%22:[],%22ignoreType%22:[],%22categories%22:[],%22status%22:%22all%22,%22statusStrict%22:true,%22includeIsBought%22:false,%22user%22:%22%22,%22branch%22:%22%22,%22apartmentType%22:%22%22,%22houseType%22:%22%22,%22archiveTime%22:86400,%22page%22:1,%22grouped%22:true}'
HUURWONINGEN_DELFT_URL = 'https://www.huurwoningen.com/en/in/delft/?price=0-1750&radius=5&living_size=50'
HUURWONINGEN_RIJSWIJK_URL = 'https://www.huurwoningen.com/en/in/rijswijk/?price=0-1750&radius=5&living_size=50'
HUURWONINGEN_HAGUE_URL = 'https://www.huurwoningen.com/en/in/den-haag/?price=0-1750&radius=5&living_size=50'

# The findall_kwargs for each URL to extract the rental count
VERRA_KWARGS = {'name': 'span', 'attrs': {'class': 'realtime-listings-total'}}
RENTOLA_KWARGS = {'string': re.compile(r"(\d+)\s+properties found", re.IGNORECASE)}
FUNDA_KWARGS = {'string': re.compile(r"(\d+)\s+homes for rent", re.IGNORECASE)}
PARARIUS_KWARGS = {'string': re.compile(r"with\s+(\d+)\s+properties\s+for\s+rent", re.IGNORECASE)}
HUURWONINGEN_KWARGS = {'name': 'span', 'attrs': {'class': 'search-list-header__count'}}

# Extra regex for filtering the resulting HTML element
PARARIUS_EXTRA_REGEX = re.compile(r"with\s+(\d+)\s+properties\s+for\s+rent", re.IGNORECASE)


if __name__ == "__main__":
    with mp.Manager() as manager:
        shared_status_dict = manager.dict()

        processes = []
        for args in [
                ("PARARIUS DELFT", PARARIUS_DELFT_URL, PARARIUS_KWARGS, PARARIUS_EXTRA_REGEX),
                ("PARARIUS RIJSWIJK", PARARIUS_RIJSWIJK_URL, PARARIUS_KWARGS, PARARIUS_EXTRA_REGEX),
                ("VERRA DELFT", VERRA_DELFT_URL, VERRA_KWARGS),
                ("VERRA RIJSWIJK", VERRA_RIJSWIJK_URL, VERRA_KWARGS),
                ("VERRA HAGUE", VERRA_HAGUE_URL, VERRA_KWARGS),
                ("RENTOLA DELFT", RENTOLA_DELFT_URL, RENTOLA_KWARGS),
                ("RENTOLA RIJSWIJK", RENTOLA_RIJSWIJK_URL, RENTOLA_KWARGS),
                ("HUURWONINGEN DELFT", HUURWONINGEN_DELFT_URL, HUURWONINGEN_KWARGS),
                ("HUURWONINGEN RIJSWIJK", HUURWONINGEN_RIJSWIJK_URL, HUURWONINGEN_KWARGS),
                ("HUURWONINGEN HAGUE", HUURWONINGEN_HAGUE_URL, HUURWONINGEN_KWARGS),
                ("FUNDA", FUNDA_URL, FUNDA_KWARGS)
        ]:
            scrapper = Scrapper(
                ID=args[0],
                URL=args[1],
                findall_kwargs=args[2],
                extra_regex=args[3] if len(args) > 3 else None,
                shared_status=shared_status_dict)
            process = mp.Process(target=scrapper.scrapper_loop)
            process.start()

            processes.append(process)
            time.sleep(1)

        telegram_bot.get_updates()  # Initial call to set the offset
        try:
            while True:
                time.sleep(1)  # Keep the main thread alive
                telegram_bot.update_step(shared_status_dict)
        except KeyboardInterrupt:
            log("Main process interrupted. Stopping all scrapers...")

        for process in processes:
            process.kill()
            process.join()
