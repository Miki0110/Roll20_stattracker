import open_login as func
import schedule, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def check_for_message(driver):
    try:
        rolls = WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.XPATH, f'//div[@class="message rollresult you player--MeYzDW63pHnEnovXXkW quantumRoll"]')))
    except:
        return

    if len(read_messages) == 0:
        for roll in rolls:
            read_messages.append(str(roll.get_attribute("data-messageid")))

    for roll in rolls:
        m_id = str(roll.get_attribute("data-messageid"))
        roll_message = str(roll.get_attribute("outerText"))

        # Check if this message has been read before
        if m_id in read_messages:
            continue
        # Save the message as read
        read_messages.append(m_id)

        # Go through the actual values of the dice
        mean, pmf, cdf = func.ret_stats(roll_message)
        print(f'mean = {float(mean)}\npmf = {float(pmf)}\ncdf = {float(1-cdf)}')


# Array for saving message ids read
global read_messages
read_messages = []
# Array for saving roll values
global roll_values
roll_values = []

driver = func.start_driver()
func.startup(driver)

schedule.every(5).seconds.do(lambda: check_for_message(driver))

print("start")
while True:
    schedule.run_pending()
    time.sleep(1)
