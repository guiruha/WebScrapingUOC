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

class UrlSpider(object):
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
        # Attributes used thoughout the script
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
        print("\n [{}] Preparing Web Driver\n\n".format(str(datetime.datetime.now())[:-7]))
        # Definition of the user agent in order to avoid possible block from webmaster
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
       
       
        options = webdriver.firefox.options.Options()
        # DECOMENT THIS LINE BELOW IF YOU DO NOT WANT TO SEE THE SEARCHING PROCESS IN THE BROWSER
        options.headless = True
        # Adding user agent to the options of the Firefox webdriver. In this case we uso the GeckoDriverManager
        # which is installed in case the user running this script does not have it installed.
        options.add_argument(f"user-agent={user_agent}")
        driver = webdriver.Firefox(service=webdriver.firefox.service.Service(GeckoDriverManager().install()), options=options)
        driver.get(url)
        time.sleep(2)
        # For maximizing window in case we are not using the headless mode
        driver.maximize_window()
        driver.implicitly_wait(2)
        try:
            #Wait until warning appears and ccept cookies
            wait = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, 'onetrust-accept-btn-handler')))
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

        print("\n [{}] Driver prepared\n\n".format(str(datetime.datetime.now())[:-7]))
        
        return driver
    
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
        # take different approach to introduce the search criteria and crawl throuigh the web. The option which xpaths are
        # intellegible has been baptized as "normal_search", and the alternative web is "non_normal search".
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
        Introduces in the search grid the parameters values inputed when the script is run for the variables nº of adults, 
        children and rooms. Depending on the landing page the scraper encounters (normal_search equal to 1 or to 2) the values 
        are introduced using different methods.

        Args:
            normal_search (bool): 1 if the landing page follows legible xpaths; 0 if the xpaths are based on codes
            list_selection_numbers (list): list containing the nº of adults, children and rooms
        
        Returns:
            None
        """
        search_params = [self.adults, self.children, self.rooms]
        # As it is presented in the comments of the function above, the approach we take when crawling the Booking landing page depends on the type of 
        # web we land in. The normal_search variable (obtained from the previous function)  indicates whether the landing page is "normal" or not
        if normal_search:
            try:
                add = self.driver.find_elements(by = "xpath", value = '//*[contains(@class, "bui-button bui-button--secondary bui-stepper__add-button ")]')
                subs = self.driver.find_element(by = "xpath", value = '//*[contains(@class, "bui-button bui-button--secondary bui-stepper__subtract-button ")]')
            except:
                add = self.driver.find_elements(by="xpath", value='//*[@data-bui-ref="input-stepper-add-button"]')
                subs = self.driver.find_element(by="xpath", value='//*[@data-bui-ref="input-stepper-subtract-button"]')
            for sl_num, sch_param, index in zip(list_selection_numbers, search_params, range(len(search_params))):
                while sl_num != sch_param:
                    if sl_num < sch_param:
                        add[index].click()
                        sl_num += 1
                        
                    else:
                        subs[index].click()
                        sl_num -= 1
                if index == 1:
                    for elem in self.driver.find_elements(by = "xpath", value='//*[@name="age"]'):
                        Select(elem).select_by_value("10")
        else:
            print("NON_NORMAL SEARCH")
            add_buttons = self.driver.find_elements(by="xpath", value='//*[@class="fc63351294 a822bdf511 e3c025e003 fa565176a8 f7db01295e e1b7cfea84 d64a4ea64d"]')
            sub_button_1 = self.driver.find_elements(by="xpath", value='//*[@class="fc63351294 a822bdf511 e3c025e003 fa565176a8 f7db01295e e1b7cfea84 cd7aa7c891"]')
            sub_button_2 = self.driver.find_elements(by="xpath", value='//*[@class="fc63351294 a822bdf511 e3c025e003 fa565176a8 f7db01295e cd7aa7c891"]')
            finished = False
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
        while inputed_month != True:
            time.sleep(2)
            try:
                current_date = self.driver.find_element(by="xpath", value="//*[contains(@aria-live, 'polite')]").text
            except:
                current_date = self.driver.find_element(by = "xpath", value = "//*[contains(@class, 'ac78a73c96 ab0d1629e5')]").text
            if len(current_date) == 0:
                current_date = self.driver.find_element(by="xpath", value="//*[contains(@class, 'bui-calendar__wrapper')]")
                current_date = current_date.text.split(" ")[0:2]
                current_date[1] = str(''.join(d for d in current_date[1] if d.isdigit()))

            if month in current_date and year in current_date:
                inputed_month = True
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
        in_day, in_month, in_year = checkin.split("-")
        out_day, out_month, out_year = checkout.split("-")
            
        self.set_month_year(in_month, in_year)
        
        day_xpath = "//span[contains(@class, 'b21c1c6c83')]"
        self.driver.find_elements(by="xpath", value=day_xpath)[int(in_day)-1].click()
        
        button = "//*[contains(@class, 'd47738b911 fb1847d86a')]"
        self.driver.find_elements(by="xpath", value=button)[1].click()
        
        self.set_month_year(out_month, out_year)
            
        day_xpath = "//span[contains(@class, 'b21c1c6c83')]"
        self.driver.find_elements(by="xpath", value=day_xpath)[int(out_day)-1].click()
        
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
        
        print("\n [{}] Inputing search criteria\n\n".format(str(datetime.datetime.now())[:-7]))
        
        try:
            self.driver.find_element(by = "xpath", value='//*[@id="ss"]').send_keys(city)
        except:
            self.driver.find_element(by = "xpath", value='//*[@name="ss"]').send_keys(city)
        try:
            self.driver.find_element(by="xpath", value='//*[@data-testid="occupancy-config"]').click()
        except:
            self.driver.find_element(by = "id", value='xp__guests__toggle').click()
            
        normal_search, c_adults, c_children, c_rooms = self.get_selection_numbers()
        
        self.introduce_selection_numbers(normal_search, [c_adults, c_children, c_rooms])
        
        print("\n [{}] Moving to the listings page\n\n".format(str(datetime.datetime.now())[:-7]))
        
        try:
            self.driver.find_element(by = "xpath", value = "//*[contains(@class, 'sb-searchbox__button ')]").click()
        except:
            self.driver.find_element(by = "xpath", value = "//*[contains(@type, 'submit')]").click()
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
        
    def save_links(self, current_page):
        """
        Retrieves the links of all of the listings of each results pages and stores it in the file "listing_links.txt"

        Returns:
            None
        """
        if current_page == 1:
            with open("listing_links.txt", "w") as f:
                for block in self.get_blocks():
                    href = block.get_attribute("href")
                    f.write(f"{href}\n")
        else:
            with open("listing_links.txt", "a+") as f:
                for block in self.get_blocks():
                    href = block.get_attribute("href")
                    f.write(f"{href}\n")

    def open_hotel(self, hotel):

        #Click on the hotel link
        hotel.click()
        #self.driver.find_element(by="xpath", value='//div[@class="fcab3ed991 a23c043802"]').click()

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


    def get_hotel_data(self, count):
        #Hotel main attributes
        try:
            hotel_name = self.driver.find_element(by="xpath", value="//h2[contains(@class, ' pp-header__title']").text
        except:
            try:
                hotel_name = self.driver.find_element(by = "xpath", value = "//h2[contains(@class, 'd2fee87262 pp-header__title')]").text
            except:
                hotel_name = f"Unkown{count}"
                
        try:
            hotel_address = self.driver.find_element(by="xpath", value='//*[contains(@class, "hp_address_subtitle")]').text
        except:
            try:
                hotel_address = self.driver.find_element(by = "xpath", value = "//*[contains(@class, 'hp_address_subtitle js-hp_address_subtitle jq_tooltip')]").text
            except:
                hotel_address = self.driver.find_element(by = "xpath", value = "//*[contains(@data-node_tt_id, 'location_score_tooltip')]").text
        try:    
            hotel_score = self.driver.find_element(by="xpath", value='//*[@class="b5cd09854e d10a6220b4"]').text
        except:
            hotel_score = -1

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
        print("Hay {} habitaciones distintas".format(len(room_name)))
        for name in room_name:
            print(name.text)

        # Get the main features of the different rooms
        room_facilities_blocks = self.driver.find_elements(by="xpath", value='//div[@class="hprt-facilities-block"]')

        room_facilities_list = []
        for room in room_facilities_blocks:
            all_facilities = room.find_elements(by="xpath", value='.//div[@class="hprt-facilities-facility"]')
            facilities_list = [fac.text for fac in all_facilities]
            room_facilities_list.append(facilities_list)

        #Extract each room data
        room_number = 0
        for room in rooms:
            room_id = room.get_attribute("data-block-id")
            room_position_table = room.get_attribute("class")
            room_name_temp = room_name[room_number].text
            room_facilities = room_facilities_list[room_number]

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

        #Store the score of the hotel for the different categories
        try:
            score_box = self.driver.find_element(by="xpath", value='//div[@class="bui-spacer--larger"]//div[@class="d46673fe81"]')
            scores = score_box.find_elements(by="xpath", value='//div[@class="ee746850b6 b8eef6afe1"]')
            score_names = score_box.find_elements(by="xpath", value='//span[@class="d6d4671780"]')
        
            hotel_scores = {score_names[i].text:scores[i].text for i in range(len(scores))}
        
        except:
            hotel_scores = {"Empty": "No Data"}

        #Create a dictionary to store all the different features extracted
        hotel_dict = {}

        hotel_dict["name"] = hotel_name
        hotel_dict["address"] = hotel_address
        hotel_dict["hotel_score"] = hotel_score
        hotel_dict["hotel_description"] = hotel_description
        hotel_dict["features"] = hotel_features
        hotel_dict["room_data"] = rooms_data
        hotel_dict["hotel_scores"] = hotel_scores


        self.hotels_list.append(hotel_dict)
        time.sleep(2)
        if random.randint(1, 100) == 47:
            self.save_photos_random(2, hotel_address)

    def save_photos_random(self, num_photos, hotel_address):
        """_summary_

        Args:
            num_photos (_type_): _description_
        """
        save_path = f"hotel_images/{hotel_address}"
        try:
            os.makedirs(save_path)
        except:
            print("Directory already exists")
            pass
        self.driver.find_element(by = "xpath", value = "//a[contains(@class,'bh-photo-grid-item bh-photo-grid-thumb js-bh-photo-grid-item-see-all')]").click()
        photos = self.driver.find_elements(by = "xpath", value = "//img[contains(@class, 'bh-photo-modal-grid-image')]")
        photos_clean = [x for x in photos if x.get_attribute('src') != None]
        if len(photos_clean) == 0:
            return None
        for num in range(num_photos):
            index = random.randint(0, len(photos_clean)-1)
            src = photos[index].get_attribute('src')
            print(f"image_{num}.png")
            try:
                urllib.request.urlretrieve(src, "/".join([save_path, f"image_{num}.png"]))
            except:
                print("An error ocurred with the name of the directory")
                pass
            
    def data_to_csv(self):

        keys = self.hotels_list[0].keys()

        with open('hotels_data.csv', 'w', newline='\n') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.hotels_list)


    def main(self):
        """
        General function that comprehends the process of all the actions performed by this class and finally closes the
        selenium driver instantiated for doing so.
        
        Returns:
            None
        """
        count = 0
        self.search_listings(self.checkin, self.checkout, self.city, self.adults, self.children, self.rooms)
        try:
            wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'onetrust-accept-btn-handler')))
            self.driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
        except:
            pass

        """hotel = self.get_blocks()[0]
        tabs = self.open_hotel(hotel)
        self.get_hotel_data()
        self.close_hotel(tabs)
        time.sleep(2)"""


        current_page, end_page = self.obtain_pages()
        while current_page <= 10: #end_page:
            #self.save_links(current_page)
            hotels = self.get_blocks()

            for hotel in hotels:
                print(hotel.get_attribute('href'))
                print("\n [{}] Retrieving info from hotel {}\n\n".format(str(datetime.datetime.now())[:-7],count))
                tabs = self.open_hotel(hotel)
                self.get_hotel_data(count)
                self.close_hotel(tabs)
                count += 1
                time.sleep(2)
            
            self.data_to_csv()

            self.next_page()
            current_page += 1
            print("\n [{}] Moving to page {}\n\n".format(str(datetime.datetime.now())[:-7], current_page))
            time.sleep(10)

        self.driver.close()