import numpy as np
import time
import os
import datetime
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
        self.checkin = checkin
        self.checkout = checkout
        self.city = city
        self.adults = int(adults)
        self.children = int(children)
        self.rooms = int(rooms)
        self.url = "https://www.booking.com"
        self.driver = self.set_selenium_driver(self.url)
            
    def set_selenium_driver(self, url):
        """
        Prepares the driver through which the scraping wil be performed

        Args:
            url (str): url of the first landing page of Booking.com
            
        Returns
            driver: fully prepared selenium driver for scraping
        """
        print("\nPreparing Web Driver\n\n")
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
       
       
        options = webdriver.firefox.options.Options()
        # DECOMENT THIS IF YOU DO NOT WANT TO SEE THE SEARCHING PROCESS IN THE BROWSER
        #options.headless = True
        options.add_argument(f"user-agent={user_agent}")
        driver = webdriver.Firefox(service=webdriver.firefox.service.Service(GeckoDriverManager().install()), options=options)
        driver.get(url)
        time.sleep(2)
        driver.maximize_window() # For maximizing window 
        driver.implicitly_wait(10)
        try:
            wait = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, 'onetrust-accept-btn-handler')))
            driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
        except:
            try:
                wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'ss')))
            except:
                wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, '__bui-c3765876-1')))

        print("Driver prepared\n\n")
        
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
            print(len(add_buttons), len(sub_button_1), len(sub_button_2))
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
        is_good_month_shows = False
        while is_good_month_shows != True:
            time.sleep(2)
            current_date = self.driver.find_element(by="xpath", value="//*[contains(@aria-live, 'polite')]").text
            if len(current_date) == 0:
                current_date = self.driver.find_element(by="xpath", value="//*[contains(@class, 'bui-calendar__wrapper')]")
                current_date = current_date.text.split(" ")[0:2]
                current_date[1] = str(''.join(i for i in current_date[1] if i.isdigit()))

            if month in current_date and year in current_date:
                is_good_month_shows = True
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
        
        try:
            self.driver.find_element(by = "xpath", value = "//*[contains(@class, 'sb-searchbox__button ')]").click()
        except:
            self.driver.find_element(by = "xpath", value = "//*[contains(@type, 'submit')]").click()

        self.set_date(self.checkin, self.checkout)
        time.sleep(2)
        
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
        
    def main(self):
        """
        General function that comprehends the process of all the actions performed by this class and finally closes the
        selenium driver instantiated for doing so.
        
        Returns:
            None
        """
        self.search_listings(self.checkin, self.checkout, self.city, self.adults, self.children, self.rooms)
        try:
            wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'onetrust-accept-btn-handler')))
            self.driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
        except:
            pass
        current_page, end_page = self.obtain_pages()
        while current_page <= end_page:
            self.save_links(current_page)
            self.next_page()
            current_page += 1
            time.sleep(10)
        self.driver.close()