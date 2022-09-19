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
            return

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
                print('here')
                return

            # Go through the actual values of the dice
            print("calculating...")
            roll_inp, result, mean, pmf, cdf = dc.ret_rolls(roll_message)  # Retrieve the statistical values
            if cdf != 'unavailable':
                print(f'Player {self.name} rolls\nMean = {float(mean)}\npmf = {float(pmf)}\ncdf = {float(1 - cdf)}')
                self.cdfs.append(cdf)
                self.rolls.append(roll_inp)
                self.rolls.append(result)
                return mean, pmf, 1-cdf
            else:  # If the message contains too many dice, the cdf and pdf will be skipped
                print(f'Player {self.name} rolls\nMean = {float(mean)}')
                return mean, pmf, cdf

    # Retrieve data from the object
    def curr_stats(self):  # Returns (rolls, average roll, best roll, best roll index)
        if len(self.cdfs) == 0:
            return ['no rolls', 'no rolls', 'no rolls', -1]
        avg_roll = sum(self.cdfs) / len(self.cdfs)
        best_roll = max(self.cdfs)
        b_index = self.cdfs.index(best_roll)
        return self.rolls, avg_roll, best_roll, b_index


# A function for checking stat calls
def ret_input(driver, read_msgs, players, last_roll):
    from data import player_ids

    try:
        texts = driver.find_elements(By.XPATH, '//*[@id="textchat"]//div[contains(text(),"--stats")]')
    except:
        read_msgs = []
        return

    if len(read_msgs) == 0:
        for text in texts:
            read_msgs.append(str(text.get_attribute("data-messageid")))

    for text in texts:
        m_id = str(text.get_attribute("data-messageid"))
        text_message = str(text.get_attribute("innerText"))

        # Check if this message has been read before
        if m_id in read_msgs:
            continue
        # Save msg ID so it's skipped next time
        read_msgs.append(m_id)

        command = text_message.split("--stats ")[-1]

        # Go through possible commands
        if command in player_ids:
            p_index = int(player_ids.index(command) / 2)  # Player index
            m_output = write_stats(players[p_index])
        elif "last" == command:
            m_output = write_lastroll(last_roll)
        else:
            print("Command not recognised")
            return

        print20(driver, '‎')
        print20(driver, f'**--------------------**')
        print20(driver, m_output)
        print20(driver, f'**--------------------**')


# Function to find and write in the chat bar
def print20(driver, message):
    text_area = driver.find_element(By.XPATH, '// *[ @ id = "textchat-input"] / textarea')
    text_area.send_keys(message)
    text_area.send_keys(Keys.ENTER)


# Writing stats out in chat
def write_stats(player):
    name = player.name
    rolls, avg_roll, best_roll, b_index = player.curr_stats()

    if b_index != -1:
        m_output = f'\n**Player {name}**\nAverage roll chance (1-cdf) = **{float(1 - avg_roll)}**\nBest roll **"{rolls[b_index * 2]}' \
                   f' = {rolls[b_index * 2 + 1]}"** with a **{float((1 - best_roll) * 100)}%** chance'
    else:
        m_output = f'Player {name} has not rolled yet'
    return m_output


# Writing out the last roll seen
def write_lastroll(last_roll):
    mean, pmf, cdf = last_roll
    if cdf != "unavailable":
        m_output = f'\n**Last roll:**\nExpected Value = **{float(mean)}**\nWith a **{float(cdf)*100}%** of rolling that or higher,' \
                   f' and a **{float(pmf)*100}%** chance for the exact value.'
        return m_output
    else:
        m_output = f'\n**Last roll:**\nExpected Value = **{float(mean)}**\n' \
                   f'Unfortunatly there were too many dice to calculate the chance of that exact roll'
        return m_output