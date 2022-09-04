import open_login
import schedule, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def check_for_message(driver):
    rolls = WebDriverWait(driver, 100).until(EC.visibility_of_all_elements_located((By.XPATH, f'//div[@class="message rollresult you player--MeYzDW63pHnEnovXXkW quantumRoll"]')))

    if len(read_messages) == 0:
        for roll in rolls:
            read_messages.append(str(roll.get_attribute("data-messageid")))
        print("it was zero")

    for roll in rolls:
        m_id = str(roll.get_attribute("data-messageid"))
        roll_value = str(roll.get_attribute("outerText"))

        # Check if this message has been read before
        if m_id in read_messages:
            continue
        # Save the message as read
        read_messages.append(m_id)

        # Go through the actual values of the dice
        roll_input = roll_value.split("\n")[0].split(" ")[-1]
        roll_result = roll_value.split("=")[-1]
        print(f"roll input = {roll_input}\nreoll result = {roll_result}")


# Array for saving message ids read
global read_messages
read_messages = []
# Array for saving roll values
global roll_values
roll_values = []

driver = open_login.start_driver()
open_login.startup(driver)

schedule.every(5).seconds.do(lambda: check_for_message(driver))

while True:
    schedule.run_pending()
    time.sleep(1)


