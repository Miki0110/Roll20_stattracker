from selenium import webdriver
from pathlib import Path
from data import login_password, login_email
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

cur_dir = Path.cwd().parent.as_posix()
PATH = f"{cur_dir}/chromedriver.exe"

driver = webdriver.Chrome(PATH)
options = webdriver.ChromeOptions()

driver.get('https://roll20.net')
#WebDriverWait(driver, timeout=100)

# Find the menu dropdown menu and click it
WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.CLASS_NAME, "navbar-toggler"))).click()

# Find the sign in menu and click it
WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH,'//ul[@class="navbar-nav navbar-notifications"]//a[@id="menu-signin"]'))).click()

#write out password and login
driver.find_element(By.XPATH,'//input[@type="email"]').send_keys(login_email)
p_input = driver.find_element(By.XPATH,'//input[@type="password"]')
p_input.send_keys(login_password)

# Click signin
p_input.send_keys(Keys.ENTER)

