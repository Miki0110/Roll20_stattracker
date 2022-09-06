import playerClass as func
from data import player_ids
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

driver = func.start_driver()
func.startup(driver)

read_msgs = []

while True:
    a = 0
    texts = WebDriverWait(driver, 500).until(EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="textchat"]//div[contains(text(),"--stats")]')))

    if len(read_msgs) == 0:
        for text in texts:
            read_msgs.append(str(text.get_attribute("data-messageid")))

    for text in texts:
        m_id = str(text.get_attribute("data-messageid"))
        text_message = str(text.get_attribute("innerText"))

        # Check if this message has been read before
        if m_id in read_msgs:
            continue

        read_msgs.append(m_id)

        target_p = text_message.split("--stats ")[-1]
        print(player_ids.index(target_p))

        text_area = driver.find_element(By.XPATH,'// *[ @ id = "textchat-input"] / textarea')
        text_area.send_keys(target_p)
        text_area.send_keys(Keys.ENTER)