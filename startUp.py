from selenium import webdriver
import playerClass as func
import atexit
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


# Function for starting the chrome driver
def start_driver():
    cur_dir = Path.cwd()
    if "\\test" in str(cur_dir):
        cur_dir = Path.cwd().parent.as_posix()
        print('we in test')
    PATH = f"{cur_dir}/chromedriver.exe"
    driver = webdriver.Chrome(PATH)

    # Register the shutdown protocall
    atexit.register(lambda: exit_handler(driver))

    return driver


# Function for logging in to roll20
def loginRoll20(driver):
    from data import login_password, login_email, player_ids

    # Open the website
    driver.get('https://roll20.net')

    # Find the menu dropdown menu and click it
    WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.CLASS_NAME, "navbar-toggler"))).click()

    # Find the sign in menu and click it
    WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH,'//ul[@class="navbar-nav navbar-notifications"]//a[@id="menu-signin"]'))).click()

    #write out password and login
    driver.find_element(By.XPATH, '//input[@type="email"]').send_keys(login_email)
    p_input = driver.find_element(By.XPATH, '//input[@type="password"]')
    p_input.send_keys(login_password)

    # Click signin
    p_input.send_keys(Keys.ENTER)

    # Find player info in DATA and return the player class in an array
    players = []
    for i in range(int(len(player_ids) / 2)):
        players.append(func.Player(player_ids[int(i * 2)], player_ids[int(i * 2) + 1]))
    return players


# Function used to close down the Chromedriver
def exit_handler(driver):
    print("Closing down the Chromedriver")
    driver.quit()
