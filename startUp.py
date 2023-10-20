from selenium import webdriver
from pathlib import Path
import pickle
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

# Function to save cookies after manual login
def save_cookies(driver, path="roll20_cookies.pkl"):
    """Save session cookies to a file.

        Parameters:
        - driver: The Selenium webdriver instance.
        - path (str): Path to the file where cookies will be saved.
        """
    cookies = driver.get_cookies()
    with open(path, 'wb') as handle:
        pickle.dump(cookies, handle)


# Function to load cookies into the driver
def load_cookies(driver, path="roll20_cookies.pkl"):
    """Load session cookies from a file and add them to the driver.

        Parameters:
        - driver: The Selenium webdriver instance.
        - path (str): Path to the file from which cookies will be loaded.
    """
    with open(path, 'rb') as handle:
        cookies = pickle.load(handle)
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()


# Function for starting the chrome driver
def start_driver():
    # Check if we are in the test folder
    cur_dir = Path.cwd()
    if "\\test" in str(cur_dir):
        print('we in test')

    # Add extension to chrome
    options = webdriver.ChromeOptions()
    options.add_extension('Beyond-20.crx')
    # Start the chrome driver
    driver = webdriver.Chrome(options=options)

    if os.path.exists("roll20_cookies.pkl"):
        driver.get('https://roll20.net')
        load_cookies(driver)

        # Maximum retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Wait for a unique element of the logged-in page.
                element_present = EC.presence_of_element_located((By.CLASS_NAME, 'avatar'))
                WebDriverWait(driver, 5).until(element_present)
                save_cookies(driver)
                break  # Exit the loop if successful
            except TimeoutException:
                if attempt < max_retries - 1:  # Don't print for the last attempt
                    print(f"Attempt {attempt + 1} failed. Retrying...")
                    load_cookies(driver)
                    driver.refresh()
                else:
                    print(f"Attempt {attempt + 1} failed.")
                    print("All attempts to auto-login failed. Please log in manually.")
                    WebDriverWait(driver, 120).until(element_present)
    else:
        print("No cookies found. Please log in manually.")
        driver.get('https://roll20.net')
        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'avatar'))
            WebDriverWait(driver, 60).until(element_present)
            save_cookies(driver)
        except TimeoutException:
            print("Timed out waiting for page to load")
    return driver
