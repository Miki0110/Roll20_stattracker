from selenium import webdriver
from pathlib import Path

cur_dir = Path.cwd().parent.as_posix()
PATH = f"{cur_dir}/chromedriver.exe"

driver = webdriver.Chrome(PATH)
options = webdriver.ChromeOptions()


driver.get('https://roll20.net')
print(driver.page_source)
