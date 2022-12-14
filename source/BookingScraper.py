# IMPORTING NECESSARY LIBRARIES
import numpy as np
import time
import csv
from collections import defaultdict
import os
import datetime
import random
import urllib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

# DEFINITION OF THE SPIDER CLASS
class BookingSpider(object):
    ##-----------------------------------------------------------------------------##
    ##              SET UP OF THE WEBDRIVER AND ENTERING LANDING PAGE              ##
    ##-----------------------------------------------------------------------------##
    def __init__(self, checkin, checkout, city, adults, children, rooms):
        """
        Initiates the instance of the class

        Args:
            checkin (str): day of checkin with format "%d-%m-%Y" 
            checkout (str): day of checkout with format "%d-%m-%Y"
            city (str): city where the rooms has to be located
            adults (int): number of adults
            children (int): number of children
            rooms (int): number of rooms
            
        Returns: 
            None
        """
        # Attributes used throughout the script
        self.checkin = checkin
        self.checkout = checkout
        self.city = city
        self.adults = int(adults)
        self.children = int(children)
        self.rooms = int(rooms)
        self.url = "https://www.booking.com"
        self.driver = self.set_selenium_driver(self.url)
        self.hotels_list = []
            
    def set_selenium_driver(self, url):
        """
        Prepares the driver through which the scraping wil be performed

        Args:
            url (str): url of the first landing page of Booking.com
            
        Returns
            driver: fully prepared selenium driver for scraping
        """
        print("\n [{}] | INFO | Preparing Web Driver\n\n".format(str(datetime.datetime.now())[:-7]))
        # Definition of the user agent in order to avoid possible block from webmaster
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
       
       
        options = webdriver.firefox.options.Options()
        # DECOMENT THIS LINE BELOW IF YOU DO NOT WANT TO SEE THE SEARCHING PROCESS IN THE BROWSER
        # options.headless = True
        # Adding user agent to the options of the Firefox webdriver. In this case we use the GeckoDriverManager
        # which is installed in case the user running this script does not have it installed.
        options.add_argument(f"user-agent={user_agent}")
        driver = webdriver.Firefox(service=webdriver.firefox.service.Service(GeckoDriverManager().install()), options=options)
        driver.get(url)
        time.sleep(3)
        # For maximizing window in case we are not using the headless mode
        driver.maximize_window()
        try:
            #Wait until warning appears and accept cookies
            wait = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'onetrust-accept-btn-handler')))
            driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
        # IN case the cookies policy button is not found the script waits until it can introduce the search criteria in the web page searcher
        # In particular id "ss" references the place where the name of the city is introduced.
        except:
            try:
                wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'ss')))
            except:
                wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, '__bui-c3765876-1')))
        
        try:
            # Click on the language button
            driver.find_elements(by="xpath", value='//button[@data-modal-id="language-selection"]')[0].click()

            # Change language
            driver.find_elements(by="xpath", value='//a[@class="bui-list-item bui-list-item--size-small " and @data-lang="en-us"]')[0].click()

        except:
            driver.find_elements(by="xpath", value='//a[@data-lang="en-us"]')[0].click()
        
        time.sleep(5)

        #Close google banner
        try:
            #Change to the pop-up window
            driver.switch_to.frame(driver.find_element(by="xpath", value="//div[@id='google-one-tap-wrapper']//iframe"))
            driver.find_element(by="xpath", value='//div[@id="close"]').click()

            #Return to the original window
            driver.switch_to.default_content()

            time.sleep(2)

        except Exception as e:
            print(e)

        print("\n [{}] | INFO | Driver prepared\n\n".format(str(datetime.datetime.now())[:-7]))
        
        return driver
    
    ##-----------------------------------------------------------------------------##
    ##            INPUTING SEARCH PARAMETERS AND SEARCHING FOR RESULTS             ##
    ##-----------------------------------------------------------------------------##
    
    def get_selection_numbers(self):
        """
        Checks which alternative landing page is being scraped and obtains the number of adults
        children and rooms in the parameter search grid.
        
        Args:
            None
        
        Returns:
            normal_search (bool): 1 if the landing page follows legible xpaths; 0 if the xpaths are based on codes
            c_adults (int): number of adults found by default in the search grid
            c_children (int): number of children found by default in the search grid
            c_rooms (int): number of rooms found by default in the search grid
        """
        # As Booking.com use different web configuration (we believe they are used for A/B testing), everytime you connect
        # with an scrapper in the web page you land randomly in one of the two options we have encountered. Therefore, we
        # take different approaches to introduce the search criteria and crawl throuigh the web. The option which xpaths are
        # readable has been baptized as "normal_search", and the alternative web is "non_normal search".
        if self.driver.find_elements(by="xpath", value='//*[@data-adults-count=""]') != []:
            normal_search = True
            c_adults = self.driver.find_element(by="xpath", value='//*[@data-adults-count=""]').text.split(" ")[0]
            c_children = self.driver.find_element(by="xpath", value='//*[@data-children-count=""]').text.split(" ")[0]
            c_rooms = self.driver.find_element(by="xpath", value='//*[@data-room-count=""]').text.split(" ")[0]
        else:
            normal_search = False
            c_adults, c_children, c_rooms = self.driver.find_elements(by = "xpath", value = "//*[@class='d47738b911 b7d08821c3']")[0].text.split(" ")[::3]
        
        return normal_search, int(c_adults), int(c_children), int(c_rooms)
        
    def introduce_selection_numbers(self, normal_search, list_selection_numbers):
        """
        Introduces in the search grid the parameter values inputed when the script is run for the variables n?? of adults, 
        children and rooms. Depending on the landing page the scraper encounters (normal_search equal to 1 or to 0) the values 
        are introduced using different methods.

        Args:
            normal_search (bool): 1 if the landing page follows legible xpaths; 0 if the xpaths are based on codes
            list_selection_numbers (list): list containing the n?? of adults, children and rooms
        
        Returns:
            None
        """
        # Introducing search parameters in list
        search_params = [self.adults, self.children, self.rooms]
        # As it is presented in the comments of the function above, the approach we take when crawling the Booking landing page depends on the type of 
        # web we land in. The normal_search variable (obtained from the previous function) indicates whether the landing page is "normal" or not
        if normal_search:
            try:
                # Find a list of add and substract buttons
                add = self.driver.find_elements(by = "xpath", value = '//*[contains(@class, "bui-button bui-button--secondary bui-stepper__add-button ")]')
                subs = self.driver.find_element(by = "xpath", value = '//*[contains(@class, "bui-button bui-button--secondary bui-stepper__subtract-button ")]')
            except:
                add = self.driver.find_elements(by="xpath", value='//*[@data-bui-ref="input-stepper-add-button"]')
                subs = self.driver.find_element(by="xpath", value='//*[@data-bui-ref="input-stepper-subtract-button"]')
            for sl_num, sch_param, index in zip(list_selection_numbers, search_params, range(len(search_params))):
                # while the number of the selection number is not equal to the search parameter the process continues by adding or substracting
                # one more unit of children, adults or rooms.
                while sl_num != sch_param:
                    if sl_num < sch_param:
                        add[index].click()
                        sl_num += 1
                        
                    else:
                        subs[index].click()
                        sl_num -= 1
                # In the case there are children in the search parameters, we input the age of 10 (to avoid making the code excesively complex)
                # due to the fact that we think it won't change the results too much.
                if index == 1:
                    for elem in self.driver.find_elements(by = "xpath", value='//*[@name="age"]'):
                        Select(elem).select_by_value("10")
        else:
            print("NON_NORMAL SEARCH")
            # We extract in this case a list of buttons
            add_buttons = self.driver.find_elements(by="xpath", value='//*[@class="fc63351294 a822bdf511 e3c025e003 fa565176a8 f7db01295e e1b7cfea84 d64a4ea64d"]')
            sub_button_1 = self.driver.find_elements(by="xpath", value='//*[@class="fc63351294 a822bdf511 e3c025e003 fa565176a8 f7db01295e e1b7cfea84 cd7aa7c891"]')
            sub_button_2 = self.driver.find_elements(by="xpath", value='//*[@class="fc63351294 a822bdf511 e3c025e003 fa565176a8 f7db01295e cd7aa7c891"]')
            finished = False
            # In this case we perform the same process, described in the normal search but with certain adaptations, as the add and substract buttons do not appear
            # using the same codes
            while finished == False:
                ## ADULTS
                sl_num = list_selection_numbers[0]
                while sl_num != search_params[0]:
                    if list_selection_numbers[0] < search_params[0]:
                        add_buttons[0].click()
                        sl_num += 1
                    else:
                        sub_button_1.click()
                        sl_num -= 1
                ## CHILDREN DOES NOT WORK BY THE TIME IF WE LAND THIS ALTERNATIVE WEB PAGE, SO IT IS COMMENTED
                # This is one challenge we could not overcome, so in case we land in a non-normal search children are not introduced in the search criteria
                sl_num = list_selection_numbers[1]
                #while sl_num != search_params[1]:
                #    if list_selection_numbers[1] < search_params[1]:
                #        self.driver.implicitly_wait(2)
                #        add_buttons[1].click()
                #        sl_num += 1
                #    else:
                #        subs_button_2[0].click()
                #        sl_num -= 1
                #elems = self.driver.find_elements(by="xpath", value="//select[contains(@name, 'age')]")
                #for i in range(len(elems)):
                #    elems[i].find_element(by="xpath", value="./option[contains(@value, '10')]").click()
                ## ROOMS
                sl_num = list_selection_numbers[2]
                while sl_num != search_params[2]:
                    if list_selection_numbers[2] < search_params[2]:
                        add_buttons[2].click()
                        sl_num += 1
                    else:
                        sub_button_2[1].click()
                        sl_num -= 1
                finished = True

    def set_month_year(self, month, year):
        """
        Navigates through the calendar of Booking.com so as to select the correct month and year of checking and checkout, that is to say,
        the ones that are inputed when running the script.

        Args:
            month (str): month of checkin/checkout
            year (str): year of checkin/checkout
        
        Returns:
            None
        """
        inputed_month = False
        # While the inputed month does not equal the month that is shown in the calendar the process does not stop
        while inputed_month != True:
            try:
                # We obtain the name of the month and year in the calendar (the left calendar of the two that are displayed in the page)
                current_date = self.driver.find_element(by="xpath", value="//*[contains(@aria-live, 'polite')]").text
            except:
                # If it does not find the calendar the page is refreshed and the month name and the year is checked again
                self.driver.navigate().refresh()
                time.sleep(5)
                current_date = self.driver.find_element(by="xpath", value="//*[contains(@aria-live, 'polite')]").text
            if len(current_date) == 0:
                # We extract the month and the year and place it in a list
                current_date = self.driver.find_element(by="xpath", value="//*[contains(@class, 'bui-calendar__wrapper')]")
                current_date = current_date.text.split(" ")[0:2]
                current_date[1] = str(''.join(d for d in current_date[1] if d.isdigit()))
            
            # if the month and the year inputed are in the list we created, the variable that makes the while continue is change 
            # to stop it
            if month in current_date and year in current_date:
                inputed_month = True
            # If the month and the year are not in the list, we click in the arrow to advance to the next calendar
            else:
                try:
                    self.driver.find_element(by="xpath", value="//button[contains(@class, 'c9fa5fc96d be298b15fa')]").click()
                except:
                    self.driver.find_element(by="xpath", value= "//*[local-name()='div' and contains(@class, 'bui-calendar__control bui-calendar__control--next')]").click()
                    
    def set_date(self, checkin, checkout):
        """
        Navigates through the calendar of Booking.com so as to select the correct day of checking and checkout, that is to say,
        the ones that are inputed when running the script.

        Args:
            checkin (str): day of checkin with format "%d-%m-%Y" 
            checkout (str): day of checkout with format "%d-%m-%Y"
        
        Returns:
            None
        """
        
        # Create variables for day, month and year for checkin and checkout
        in_day, in_month, in_year = checkin.split("-")
        out_day, out_month, out_year = checkout.split("-")
        
        # Set the correct year and month using the previous function
        self.set_month_year(in_month, in_year)
        
        # Click on the day (the day is always one position before its number)
        self.driver.find_elements(by="xpath", value="//span[contains(@class, 'b21c1c6c83')]")[int(in_day)-1].click()
        
        # Click the button to open the other calendar (checkout)
        self.driver.find_elements(by="xpath", value="//*[contains(@class, 'd47738b911 fb1847d86a')]")[1].click()
        
        # Set the correct year and month using the previous function
        self.set_month_year(out_month, out_year)
        
        # Click on the day (the day is always one position before its number)    
        self.driver.find_elements(by="xpath", value="//span[contains(@class, 'b21c1c6c83')]")[int(out_day)-1].click()
        
    def search_listings(self, checkin, checkout, city, adults, children, rooms):
        """
        General function that comprehends all the functions and selenium fucntionalities related to selecting search parameters 
        and clicking on search buttons

        Args:
            checkin (str): day of checkin with format "%d-%m-%Y" 
            checkout (str): day of checkout with format "%d-%m-%Y"
            city (str): city where the rooms has to be located
            adults (int): number of adults
            children (int): number of children
            rooms (int): number of rooms
        """
        
        print("\n [{}] | INFO | Inputing search criteria\n\n".format(str(datetime.datetime.now())[:-7]))
        
        # Put the city in the search engine of booking com (lots of tries and exceptions because it fails sometimes)
        try:
            self.driver.find_element(by = "xpath", value='//*[@id="ss"]').send_keys(city)
        except:
            try:
                self.driver.find_element(by = "xpath", value='//*[@id="__bui-c308021-1"]').send_keys(city)
            except:
                self.driver.find_element(by = "xpath", value='//*[@name="ss"]').send_keys(city)
        try:
            self.driver.find_element(by="xpath", value='//*[@data-testid="occupancy-config"]').click()
        except:
            self.driver.find_element(by = "id", value='xp__guests__toggle').click()
            
        # Obtain the selection numbers from the search engine bar
        normal_search, c_adults, c_children, c_rooms = self.get_selection_numbers()
        
        # Introduce selection numbers
        self.introduce_selection_numbers(normal_search, [c_adults, c_children, c_rooms])
        
        print("\n [{}] | INFO | Moving to the listings page\n\n".format(str(datetime.datetime.now())[:-7]))
        
        # Click the search button
        try:
            self.driver.find_element(by = "xpath", value = "//*[contains(@class, 'sb-searchbox__button ')]").click()
        except:
            try:
                self.driver.find_element(by = "xpath", value = "//*[contains(@type, 'submit')]").click()
            except:
                self.driver.find_element(by="xpath", value="//button[contains(@class, 'fc63351294 a822bdf511 d4b6b7a9e7 cfb238afa1 af18dbd5a4 f4605622ad aa11d0d5cd')]").click()
        # If the Genius ad appears close it, if not pass
        try:
            wait = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS, 'fc63351294 a822bdf511 e3c025e003 fa565176a8 f7db01295e ae1678b153')))
            self.driver.find_element(by="xpath", value="//button[contains(@class, 'fc63351294 a822bdf511 e3c025e003 fa565176a8 f7db01295e ae1678b153'')]").click()
        except:
            pass
        # Introduce data in the calendar using the previously defined function
        try:
            self.set_date(self.checkin, self.checkout)
            time.sleep(2)
        except:
            try:
                self.driver.find_element(by = "xpath", value = "//*[contains(@class, 'd47738b911 fb1847d86a')]").click()
                self.set_date(self.checkin, self.checkout)
            except:
                self.driver.find_element(by = "xpath", value = "//*[contains(@data-testid, 'date-display-field-start')]").click()
                self.set_date(self.checkin, self.checkout)
        
        # Click in the search button below the calendars
        button = f"//*[contains(@class, 'fc63351294 a822bdf511 d4b6b7a9e7 f7db01295e af18dbd5a4 f4605622ad c827b27356')]"
        self.driver.find_element(by="xpath", value=button).click()

    def get_blocks(self):
        """
        Obtains the blocks containing the information of each of the listing appearing in each of the results pages after
        inputing all the selection criteria.

        Returns:
            None
        """
        return self.driver.find_elements(by="xpath", value="//a[contains(@class, 'e13098a59f')]")
        
    def obtain_pages(self):
        """
        Obtains the number of the first and last page of the results provided after inputing all the seleciton criteria.

        Returns:
            start (int): number of the firt page of results (usually "1").
            end (int): number of the last page of results.
        """
        start = int(self.driver.find_element(by="xpath", value="//li[contains(@class, 'f32a99c8d1 ebd02eda9e')]").text)
        end = int(self.driver.find_elements(by="xpath", value="//li[contains(@class, 'f32a99c8d1')]")[-1].text)
        return start, end
    
    def next_page(self):
        """
        Clicks on the results page button that leads to the next page
        
        Returns:
            None
        """
        self.driver.find_element(by = "xpath", value = "//*[contains(@aria-label, 'Next page')]").click()
    
    ##-----------------------------------------------------------------------------##
    ##          RETRIEVING DATA FROM ALL THE HOTELS FOUND IN THE SERARCH           ##
    ##-----------------------------------------------------------------------------##

    def open_hotel(self, hotel):

        #Click on the hotel link
        hotel.click()

        #Wait for the tab to open
        wait = WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))

        #Switch tabs
        tabs = self.driver.window_handles
        self.driver.switch_to.window(tabs[1])

        return tabs

    def close_hotel(self, tabs):

        #Close current tab
        self.driver.close()

        #Return to the main tab
        self.driver.switch_to.window(tabs[0])


    def get_hotel_data(self, count, current_page, in_page_count):
        #Hotel main attributes
        # All info has been retieved using several try and except due to the fact that the webdriver sometimes finds difficulties when searching
        # the xpath
        # Hotel name
        try:
            hotel_name = self.driver.find_element(by="xpath", value="//h2[contains(@class, ' pp-header__title']").text
        except:
            try:
                hotel_name = self.driver.find_element(by = "xpath", value = "//h2[contains(@class, 'd2fee87262 pp-header__title')]").text
            except:
                try:
                    hotel_name = self.driver.find_element(by="xpath", value='//h2[@class="d2fee87262 pp-header__title"]').text
                except:
                    try:
                        hotel_name = self.driver.find_element(by="xpath", value="//div[@data-capla-component='b-property-web-property-page/PropertyHeaderName']").text
                    except:
                        hotel_name = f"Unkown{count}"
        
        # Hotel address
        try:
            hotel_address = self.driver.find_element(by="xpath", value='//*[contains(@class, "hp_address_subtitle")]').text
        except:
            try:
                hotel_address = self.driver.find_element(by = "xpath", value = "//*[contains(@class, 'hp_address_subtitle js-hp_address_subtitle jq_tooltip')]").text
            except:
                try:
                    hotel_address = self.driver.find_element(by = "xpath", value = "//*[contains(@data-node_tt_id, 'location_score_tooltip')]").text
                except:
                    hotel_address = f"Unknown{count}"

        # Hotel score
        try:
            hotel_score = self.driver.find_element(by="xpath", value="//div[@class='page-section js-k2-hp--block k2-hp--featured_reviews']//div[@class='b5cd09854e d10a6220b4']").text
        except:
            try:
                hotel_score = self.driver.find_element(by="xpath", value='//*[@class="b5cd09854e d10a6220b4"]').text
            except:
                try:
                    hotel_score = self.driver.find_element(by="xpath", value="//div[@class='b5cd09854e d10a6220b4']").text
                except:
                    hotel_score = -1
        
        # Hotel coordinates
        try:
            hotel_coordinates = self.driver.find_element(by="xpath", value='//a[@id="hotel_address"]').get_attribute(
                "data-atlas-latlng")
        except:
            hotel_coordinates = "NA"

        #Hotel features
        hotel_features = []
        hotel_all_features = self.driver.find_elements(by="xpath", value='//div[@class="db29ecfbe2 c21a2f2d97 fe87d598e8"]')
        for feature in hotel_all_features:
            hotel_features.append(feature.text)

        #Hotel description
        hotel_description = []
        hotel_all_description = self.driver.find_elements(by="xpath", value='//div[@id="property_description_content"]//p')
        for par in hotel_all_description:
            hotel_description.append(par.text)

        #Different rooms
        rooms = self.driver.find_elements(by="xpath", value='//table[contains(@class, "hprt-table")]//tr[contains(@class, "js-rt-block-row e2e-hprt-table-row ")]')
        rooms_data = {}

        # Get the name of the different rooms
        room_name = self.driver.find_elements(by="xpath", value='//span[@class="hprt-roomtype-icon-link "]')

        # Get the main features of the different rooms
        room_facilities_blocks = self.driver.find_elements(by="xpath", value='//div[@class="hprt-facilities-block"]')

        # Get the list of all room facilities
        room_facilities_list = []
        for room in room_facilities_blocks:
            all_facilities = room.find_elements(by="xpath", value='.//div[@class="hprt-facilities-facility"]')
            facilities_list = [fac.text for fac in all_facilities]
            room_facilities_list.append(facilities_list)

        # Bed type
        bed_types_elements = self.driver.find_elements(by="xpath", value='//div[@class="hprt-roomtype-bed"]')
        bed_types_list = []

        for room_bed in bed_types_elements:
            try:
                beds = room_bed.find_elements(by="xpath", value='.//span')
                bed_name = ""
                for one_bed in beds:
                    if one_bed.text == "":
                        continue
                    else:
                        bed_name += one_bed.text + "/ "

            except Exception as e:
                pass

            try:
                choice = room_bed.find_element(by="xpath", value='.//input')
                if choice.get_attribute("type") == "radio":
                    bed_name += "/multiple choice/"
            except:
                pass

            if bed_name == "":
                pass
            else:
                bed_types_list.append(bed_name)

        # Extract each room data
        room_number = 0
        for room in rooms:
            room_id = room.get_attribute("data-block-id")
            room_position_table = room.get_attribute("class")
            room_name_temp = room_name[room_number].text
            room_facilities = room_facilities_list[room_number]
            room_bed_type = bed_types_list[room_number]

            # When it is the last row for one room, the room number is changed
            if "hprt-table-last-row" in room_position_table:
                room_number += 1

            rooms_data[room_id] = {}

            room_price = self.driver.find_element(by="xpath", value='//tr[contains(@data-block-id, "{}")]//span[contains(@class, "prco-valign-middle-helper")]'.format(room_id)).text
            room_capacity = self.driver.find_element(by="xpath", value='//tr[contains(@data-block-id, "{}")]//span[contains(@class, "bui-u-sr-only")]'.format(room_id)).text

            room_options_all_objects = self.driver.find_elements(by="xpath", value='//tr[contains(@data-block-id, "{}")]//td[contains(@class, " hprt-table-cell hprt-table-cell-conditions ")]//div[contains(@class, "bui-list__description")]'.format(room_id))
            room_options = []
            for room_option in room_options_all_objects:
                room_options.append(room_option.text)

            # Add features to the room data dictionary
            rooms_data[room_id]["room_name"] = room_name_temp
            rooms_data[room_id]["room_price"] = room_price
            rooms_data[room_id]["room_capacity"] = room_capacity
            rooms_data[room_id]["room_options"] = room_options
            rooms_data[room_id]["room_facilities"] = room_facilities
            rooms_data[room_id]["room_bed_type"] = room_bed_type

        #Store the score of the hotel for the different categories
        try:
            score_box = self.driver.find_element(by="xpath", value='//div[@class="bui-spacer--larger"]//div[@class="d46673fe81"]')
            scores = score_box.find_elements(by="xpath", value='//div[@class="ee746850b6 b8eef6afe1"]')
            score_names = score_box.find_elements(by="xpath", value='//span[@class="d6d4671780"]')
        
            hotel_scores = {score_names[i].text:scores[i].text for i in range(len(scores))}
        
        except:
            hotel_scores = {"Empty": "No Data"}

        #Search date
        search_date = datetime.datetime.today().strftime('%Y-%m-%d')

        # Create a dictionary to store all the different features extracted (we include also the search parameters
        # as we plan to use that information in the following assignment)
        hotel_dict = {"name": hotel_name, "city": self.city, "check-in":self.checkin, "adults": self.adults, "children": self.children,
                      "check-out": self.checkout, "num_rooms": self.rooms, "address": hotel_address, "hotel_coordinates": hotel_coordinates,
                      "hotel_score": hotel_score, "hotel_scores": hotel_scores, "hotel_description": hotel_description,
                      "features": hotel_features, "room_data": rooms_data, "page_count": count, "current_page": current_page,
                      "in_page_count": in_page_count, "search_date": search_date}

        self.hotels_list.append(hotel_dict)
        time.sleep(5)
        # In order to avoid downloading all photos, we use the random library to only download photos from 
        # 1/50 of the hotels scraped.
        if random.randint(1, 50) == 5:
            self.save_photos_random(2, hotel_address)

    def save_photos_random(self, num_photos, hotel_address):
        """Opens the grid of photos for each hotel scrapped and downloads only a determined number of photos of them

        Args:
            num_photos (int): number of photos to download per hotel
            
        Returns:
            None
        """
        save_path = f"dataset/hotel_images/{hotel_address}"
        # Create a directory if it does not exists
        try:
            os.makedirs(save_path)
        except:
            print("Directory already exists")
            pass
        # Open the photos grid
        self.driver.find_element(by = "xpath", value = "//a[contains(@class,'bh-photo-grid-item bh-photo-grid-thumb js-bh-photo-grid-item-see-all')]").click()
        photos = self.driver.find_elements(by = "xpath", value = "//img[contains(@class, 'bh-photo-modal-grid-image')]")
        # Some elements retrieved in the previous line are empty so we eliminate them if there is no link of the photo
        photos_clean = [x for x in photos if x.get_attribute('src') != None]
        # If there are not photos the directory will be empty
        if len(photos_clean) == 0:
            return None
        # For a range determined by the variable num_photos we select a random photo of the grid in each iteration
        for num in range(num_photos):
            index = random.randint(0, len(photos_clean)-1)
            src = photos[index].get_attribute('src')
            print(f"image_{num}.png")
            try:
                urllib.request.urlretrieve(src, "/".join([save_path, f"image_{num}.png"]))
            except:
                print("An error ocurred with the name of the directory")
                pass
            
    ##-----------------------------------------------------------------------------##
    ##                     SAVING THE RESULTS IN A CSV FILE                        ##
    ##-----------------------------------------------------------------------------##
    
    def data_to_csv(self):

        keys = self.hotels_list[0].keys()

        if not os.path.isdir("dataset/"):
            os.makedirs("dataset/")
            
        if os.path.isfile('dataset/hotels_data.csv'):
            with open('dataset/hotels_data.csv', 'a+', newline='\n') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writerows(self.hotels_list)

        else:
            with open('dataset/hotels_data.csv', 'w', newline='\n') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(self.hotels_list)
        
        self.hotels_list = []
                
    ##-----------------------------------------------------------------------------##
    ##                        RUN ALL THE PROCESS AT ONCE                          ##
    ##-----------------------------------------------------------------------------##
    
    def main(self):
        """
        General function that comprehends the process of all the actions performed by this class and finally closes the
        selenium driver instantiated for doing so.
        
        Returns:
            None
        """
        count = 0
        print(self.city)
        self.search_listings(self.checkin, self.checkout, self.city, self.adults, self.children, self.rooms)
        try:
            wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'onetrust-accept-btn-handler')))
            self.driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
        except:
            pass
        
        current_page, end_page = self.obtain_pages()
        
        #If we wanted to get all the listings from this search we would use end_page instead of 5 (but for our purposes, and in order
        # to not create a csv with too much weight we extract data only from the first 5 pages)
        while current_page <= 5:
            hotels = self.get_blocks()
            in_page_count = 0

            for hotel in hotels:
                print("\n [{}] | INFO | Retrieving info from hotel {}\n\n".format(str(datetime.datetime.now())[:-7],count))
                tabs = self.open_hotel(hotel)
                self.get_hotel_data(count, current_page, in_page_count)
                self.close_hotel(tabs)
                count += 1
                in_page_count += 1
                time.sleep(3)
            
            # After retrieving data of each hotels from the current pages, the info is saved  
            self.data_to_csv()

            self.next_page()
            current_page += 1
            print("\n [{}] | INFO | Moving to page {}\n\n".format(str(datetime.datetime.now())[:-7], current_page))
            time.sleep(10)

        self.driver.close()