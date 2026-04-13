# BlazeDemo Flight Automation Framework

A lightweight Python test automation framework using pytest and Selenium WebDriver to automate the "Find Flights" flow on https://blazedemo.com/

## Project Structure

```
GitHubCopilotDemo/
├── conftest.py                 # Pytest fixtures for driver and base_url
├── requirements.txt            # Python dependencies
├── pages/                      # Page Object Model
│   ├── HomePage.py            # Home page interactions
│   └── FlightsPage.py         # Flights results page interactions
├── tests/
│   └── test_find_flights.py   # Test cases
├── utils/
│   └── WebDriverUtils.py      # Utility functions
└── allure-results/            # Allure report results
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd GitHubCopilotDemo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Tests

Run all tests:
```bash
pytest tests/
```

Run with verbose output:
```bash
pytest tests/ -v
```

## Generating Allure Report

After running tests:
```bash
allure generate allure-results/ -o allure-report/
allure open allure-report/
```

## Technologies Used

- **Selenium WebDriver** - Browser automation
- **Pytest** - Test framework
- **Allure** - Report generation
- **WebDriver Manager** - Automatic ChromeDriver management

