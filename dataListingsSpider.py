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

class DataSpider(object):
    def __init__(self, url):
        """
        """
        self.url = url
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
        options.headless = True
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
    
    def obtain_data(self):
        price = self.driver.find_element(by = "xpath", value="//span[contains(@class, 'prco-valign-middle-helper')]").text.split(" ")[1]
        print("Price: ", price)
        tags = self.driver.find_elements(by = "xpath", value="//div[contains(@class, 'db29ecfbe2 c21a2f2d97 fe87d598e8')]")
        tags_list = list(map(lambda x: x.text, tags))
        print("Includes: ", tags_list)
        grade = self.driver.find_element(by = "xpath", value="//div[contains(@class, 'b5cd09854e d10a6220b4')]")
        print("Grade: ", grade.text)
        beds = self.driver.find_elements(by = "xpath", value="//span[contains(@class, 'm-rs-bed-display__bed-type-name')]")
        beds_list = list(filter(lambda x: x != "", map(lambda x: x.text, beds)))
        print("Nº of beds: ", beds_list)
        reviews = self.driver.find_element(by = "xpath", value="//span[contains(@class, 'b5cd09854e c90c0a70d3 db63693c62')]").text.split(" ")[2]
        print("Nº of reviews: ", reviews)
        coordinates = self.driver.find_element(by = "xpath", value="//a[contains(@id, 'hotel_address')]").get_attribute("data-atlas-latlng")
        print("Coordinates: ", coordinates)
        subcat = self.driver.find_elements(by = "xpath", value="//span[contains(@class, 'd6d4671780')]")
        subcat_list = list(filter(lambda x: x != "", map(lambda x: x.text, subcat)))
        subgrades = self.driver.find_elements(by = "xpath", value="//div[contains(@class, 'ee746850b6 b8eef6afe1')]")
        subgrades_list = list(filter(lambda x: x != "", map(lambda x: x.text, subgrades)))
        subgrading = [f"{x}:{y}" for x,y in zip(subcat_list, subgrades_list)]
        print(subgrading)
        self.driver.quit()
        
        
"""with open("listing_links.txt", "r") as links:
        for ind, link in enumerate(links):
            if ind == 1:
                break
            booking_data = DataSpider(link)    
            booking_data.obtain_data()"""