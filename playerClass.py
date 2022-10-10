from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import dice_calculations as dc


# Class used to define each player and their message ids
class Player:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.read_msg = []
        self.rolls = []
        self.cdfs = []

    def check_roll(self, driver):
        try:
            rolls = driver.find_elements(By.XPATH, f'//div[@data-playerid="{self.id}"]')
        except:
            # If there are no rolls, just return with nothing
            self.read_msg = []
            return 0

        if len(self.read_msg) == 0:  # If it's the first time the program is called, don't read old messages
            for roll in rolls:
                self.read_msg.append(str(roll.get_attribute("data-messageid")))

        for roll in rolls:  # Go through all the messages
            m_id = str(roll.get_attribute("data-messageid"))  # message ID
            roll_message = str(roll.get_attribute("innerText"))  # Roll result

            # Check if this message has been read before
            if m_id in self.read_msg:
                continue
            # Save the message as read
            self.read_msg.append(m_id)

            # In case there are no rolls in the message
            if roll_message.split("rolling ")[-1].split("\n")[0].find("d") == -1:
                return 0

            # Go through the actual values of the dice
            print("calculating...")
            out = dc.ret_rolls(roll_message)  # Retrieve the statistical values
            if out != -1:
                roll_inp, result, mean, pmf, cdf = out
                print(f'Player {self.name} rolls\nMean = {float(mean)}\npmf = {float(pmf)}\ncdf = {float(1 - cdf)}')
                self.cdfs.append(cdf)
                self.rolls.append(roll_inp)
                self.rolls.append(result)
                return roll_inp, result, self.name
            else:  # If the message contains too many dice, the cdf and pdf will be skipped
                print(f'Not possible')
                return 0

    # Retrieve data from the object
    def curr_stats(self):  # Returns (rolls, average roll, best roll, best roll index)
        if len(self.cdfs) == 0:
            return ['no rolls', 'no rolls', 'no rolls', -1]
        avg_roll = sum(self.cdfs) / len(self.cdfs)
        best_roll = max(self.cdfs)
        b_index = self.cdfs.index(best_roll)
        return self.rolls, avg_roll, best_roll, b_index


# Function to find and write in the chat bar
def print20(driver, message):
    text_area = driver.find_element(By.XPATH, '// *[ @ id = "textchat-input"] / textarea')
    text_area.send_keys(message)
    text_area.send_keys(Keys.ENTER)


# Retrieve dice from the already gone through dice rolls
def ret_dice(message):
    import re
    d = []
    for roll in (re.findall(r'\d+d\d+', message)):
        roll = roll.split('d')
        for i in range(int(roll[0])):
            d.append(roll[1])
    return d, int(message.split('+')[-1])
