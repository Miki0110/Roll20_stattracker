from selenium import webdriver
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os


# Function to save cookies after manual login
def save_cookies(driver, path="roll20_cookies.txt"):
    """Save session cookies to a file.

        Parameters:
        - driver: The Selenium webdriver instance.
        - path (str): Path to the file where cookies will be saved.
        """
    cookies = driver.get_cookies()
    with open(path, "w") as file:
        json.dump(cookies, file)


# Function to load cookies into the driver
def load_cookies(driver, path="roll20_cookies.txt"):
    """Load session cookies from a file and add them to the driver.

        Parameters:
        - driver: The Selenium webdriver instance.
        - path (str): Path to the file from which cookies will be loaded.
    """
    with open(path, "r") as file:
        cookies = json.load(file)
    for cookie in cookies:
        driver.add_cookie(cookie)


# Function for starting the chrome driver
def start_driver():
    cur_dir = Path.cwd()
    if "\\test" in str(cur_dir):
        print('we in test')
    driver = webdriver.Chrome()
    if os.path.exists("roll20_cookies.txt"):
        driver.get('https://roll20.net')
        load_cookies(driver)
        driver.refresh()
    return driver
