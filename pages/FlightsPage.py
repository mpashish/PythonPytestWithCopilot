from selenium.webdriver.common.by import By

class FlightsPage:
    def __init__(self, driver):
        self.driver = driver
        self.flights_table = (By.TAG_NAME, "table")
        self.choose_flight_buttons = (By.CSS_SELECTOR, "input[type='submit']")

    def are_flights_displayed(self):
        return self.driver.find_element(*self.flights_table).is_displayed()

    def get_number_of_flights(self):
        buttons = self.driver.find_elements(*self.choose_flight_buttons)
        return len(buttons)
