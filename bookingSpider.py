import numpy as np
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

class BookingSpider(object):
    def __init__(self, checkin, checkout, city, country, adults, children, rooms):
        """WRITE SUMMARY

        Args:
            checkin (_type_): _description_
            checkout (_type_): _description_
            city (_type_): _description_
            country (_type_): _description_
            adults (_type_): _description_
            children (_type_): _description_
            rooms (_type_): _description_
        """
        self.checkin = checkin
        self.checkout = checkout
        self.city = city
        self.country = country
        self.adults = int(adults)
        self.children = int(children)
        self.rooms = int(rooms)
        self.url = "https://www.booking.com"
        self.driver = self.set_selenium_driver(self.url)
            
    def set_selenium_driver(self, url):
        """_summary_

        Args:
            url (_type_): _description_
        """
        print("\nPreparing Web Driver\n\n")
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
       
       
        options = webdriver.firefox.options.Options()
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
        """_summary_
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
        """_summary_

        Args:
            normal_search (_type_): _description_
            list_selection_numbers (_type_): _description_
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
                    print(sl_num, sch_param, index)
                    if sl_num < sch_param:
                        add[index].click()
                        sl_num += 1
                    else:
                        subs[index].click()
                        sl_num -= 1
        else:
            print(len(self.driver.find_elements(by="xpath", value='//*[@class="e98c626f34"]')))
            for elem in self.driver.find_elements(by="xpath", value='//*[@class="e98c626f34"]'):
                print(elem[0])
    
    def search_listings(self, checkin, checkout, city, country, adults, children, rooms):
        """_summary_

        Args:
            city (_type_): _description_
        """
        #self.driver.find_element(by="id", value="checkin").send_keys(checkin)
        #self.driver.find_element(by="id", value="checkout").send_keys(checkout)
        try:
            self.driver.find_element(by = "xpath", value='//*[@id="ss"]').send_keys(city)
        except:
            self.driver.find_element(by = "xpath", value='//*[@name="ss"]').send_keys(city)
        #self.driver.find_element(by="id", value="country").send_keys(country)
        #self.driver.find_element(by="id", value="group_adults").send_keys(adults)
        #self.driver.find_element(by="id", value="group_children").send_keys(children)
        #self.driver.find_element(by="id", value="no_rooms").send_keys(rooms)
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
        
    def save_links(self, current_page):
        """_summary_

        Returns:
            _type_: _description_
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
    
    def get_xpath(self, xpath):
        """_summary_

        Args:
            xpath (_type_): _description_

        Returns:
            _type_: _description_
        """
        return self.driver.find_element(by="xpath", value=xpath)
    
    def get_blocks(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.driver.find_elements(by="xpath", value="//a[contains(@class, 'e13098a59f')]")
    
    def obtain_pages(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        start = int(self.driver.find_element(by="xpath", value="//li[contains(@class, 'f32a99c8d1 ebd02eda9e')]").text)
        end = int(self.driver.find_elements(by="xpath", value="//li[contains(@class, 'f32a99c8d1')]")[-1].text)
        return start, end
    
    def next_page(self):
        """_summary_
        """
        self.driver.find_element(by = "xpath", value = "//*[contains(@aria-label, 'Next page')]").click()
        
    def main(self):
        """_summary_
        """
        self.search_listings(self.checkin, self.checkout, self.city, self.country, self.adults, self.children, self.rooms)
        try:
            wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'onetrust-accept-btn-handler')))
            self.driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
        except:
            pass
        current_page, end_page = self.obtain_pages()
        while current_page < end_page:
            self.save_links(current_page)
            self.next_page()
            current_page += 1
            time.sleep(10)
        self.driver.close()