import numpy as np
import time
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
        self.adults = adults
        self.children = children
        self.rooms = rooms
        self.url = "https://www.booking.com"
        self.driver = self.set_selenium_driver(self.url)
            
    def set_selenium_driver(self, url):
        """_summary_

        Args:
            url (_type_): _description_
        """
        print("Preparing Web Driver")
        print("\n\n")
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
       
       
        options = webdriver.firefox.options.Options()
        options.headless = True
        options.add_argument(f"user-agent={user_agent}")
        driver = webdriver.Firefox(service=webdriver.firefox.service.Service(GeckoDriverManager().install()), options=options)
        driver.get(url)
        try:
            wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'ss')))
        except:
            print("An error occured, check line 50")
            time.time(10)
            self.set_selenium_driver(self.url)
        
        print("Driver prepared\n\n")
        
        return driver
    
    def search_listings(self, checkin, checkout, city, country, adults, children, rooms):
        """_summary_

        Args:
            city (_type_): _description_
        """
        try:
            self.driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
        except:
            pass
        #self.driver.find_element(by="id", value="checkin").send_keys(checkin)
        #self.driver.find_element(by="id", value="checkout").send_keys(checkout)
        self.driver.find_element(by = "xpath", value=r'//*[@id="ss"]').send_keys(city)
        #self.driver.find_element(by="id", value="country").send_keys(country)
        #self.driver.find_element(by="id", value="group_adults").send_keys(adults)
        #self.driver.find_element(by="id", value="group_children").send_keys(children)
        #self.driver.find_element(by="id", value="no_rooms").send_keys(rooms)
        self.driver.find_element(by = "xpath", value = "/html/body/div[1]/div[2]/div/form/div[1]/div[4]/div[2]/button").click()
    
    def get_links(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return list(map(lambda hotel: hotel.get_attribute("href"), self.get_names_and_links_in_cards()))
    
    def get_xpath(self, xpath):
        """_summary_

        Args:
            xpath (_type_): _description_

        Returns:
            _type_: _description_
        """
        return self.driver.find_element(by="xpath", value=xpath)
    
    def get_names_and_links_in_cards(self):
        return self.driver.find_elements(by="xpath", value="//a[contains(@class, 'e13098a59f')]")
        
    def main(self):
        self.search_listings(self.checkin, self.checkout, self.city, self.country, self.adults, self.children, self.rooms)
        print(self.get_links())
        self.driver.close()

        
if __name__ == "__main__":
    booking = BookingSpider(checkin="05-20-2022", 
                            checkout="05-23-2022", 
                            city="Barcelona", 
                            country="España", 
                            adults=2, 
                            children=1, 
                            rooms=2)
    booking.main()