from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

class HomePage:
    def __init__(self, driver):
        self.driver = driver
        self.departure_dropdown = (By.NAME, "fromPort")
        self.destination_dropdown = (By.NAME, "toPort")
        self.find_flights_button = (By.CSS_SELECTOR, "input[type='submit']")

    def select_departure_city(self, city):
        Select(self.driver.find_element(*self.departure_dropdown)).select_by_visible_text(city)

    def select_destination_city(self, city):
        Select(self.driver.find_element(*self.destination_dropdown)).select_by_visible_text(city)

    def click_find_flights(self):
        self.driver.find_element(*self.find_flights_button).click()
