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
    
    def set_date(self, checkin, checkout):
        in_day, in_month, in_year = checkin.split("-")
        out_day, out_month, out_year = checkout.split("-")
        is_good_month_shows = False
        while is_good_month_shows != True:
            time.sleep(2)
            xpath_calendar = "//*[contains(@aria-live, 'polite')]"
            current_date = self.driver.find_element(by="xpath", value=xpath_calendar).text
            if len(current_date) == 0:
                current_date = self.driver.find_element(by="xpath", value="//*[contains(@class, 'bui-calendar__wrapper')]")
                current_date = current_date.text.split(" ")[0:2]
                current_date[1] = str(''.join(i for i in current_date[1] if i.isdigit()))

            if in_month in current_date and in_year in current_date:
                is_good_month_shows = True
            else:
                try:
                    self.driver.find_element(by="xpath", value="//button[contains(@class, 'c9fa5fc96d be298b15fa')]").click()
                except:
                    self.driver.find_element(by="xpath", value= "//*[local-name()='div' and contains(@class, 'bui-calendar__control bui-calendar__control--next')]").click()
            
        day_xpath = f"//span[contains(@class, 'b21c1c6c83')]"
        self.driver.find_elements(by="xpath", value=day_xpath)[int(in_day)-1].click()
        
        button = f"//*[contains(@class, 'd47738b911 fb1847d86a')]"
        self.driver.find_elements(by="xpath", value=button)[1].click()
            
        day_xpath = f"//span[contains(@class, 'b21c1c6c83')]"
        self.driver.find_elements(by="xpath", value=day_xpath)[int(out_day)-1].click()
        
    def search_listings(self, checkin, checkout, city, country, adults, children, rooms):
        """_summary_

        Args:
            city (_type_): _description_
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
        while current_page <= end_page:
            self.save_links(current_page)
            self.next_page()
            current_page += 1
            time.sleep(10)
        self.driver.close()