import pytest
import allure
from pages.HomePage import HomePage
from pages.FlightsPage import FlightsPage

@allure.feature("Find Flights")
class TestFindFlights:

    @allure.story("Find flights with valid cities")
    @pytest.mark.smoke
    def test_find_flights_valid(self, driver, base_url):
        driver.get(base_url)
        home_page = HomePage(driver)
        home_page.select_departure_city("Boston")
        home_page.select_destination_city("London")
        home_page.click_find_flights()
        flights_page = FlightsPage(driver)
        assert flights_page.are_flights_displayed()
        assert flights_page.get_number_of_flights() > 0

    @allure.story("Find flights with same cities")
    def test_find_flights_same_city(self, driver, base_url):
        driver.get(base_url)
        home_page = HomePage(driver)
        home_page.select_departure_city("Boston")
        home_page.select_destination_city("Boston")
        home_page.click_find_flights()
        flights_page = FlightsPage(driver)
        # Assuming it still shows flights or something, but for demo
        assert flights_page.are_flights_displayed()
