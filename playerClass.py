from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


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
            rolls = WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located(
                (By.XPATH, f'//div[@data-playerid="{self.id}"]')))
        except:
            # If there are no rolls, just return with nothing
            self.read_msg = []
            return

        if len(self.read_msg) == 0:  # If it's the first time the program is called, don't read old messages
            for roll in rolls:
                self.read_msg.append(str(roll.get_attribute("data-messageid")))

        for roll in rolls:  # Go through all the messages
            m_id = str(roll.get_attribute("data-messageid"))  # message ID
            roll_message = str(roll.get_attribute("outerText"))  # Roll result

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
            roll_inp, result, mean, pmf, cdf = ret_rolls(roll_message)  # Retrieve the statistical values
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


# Simpel index list function
def find_indexes(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]


# function for retrieving the dice rolls
def ret_rolls(roll_message):
    # Using sumpy for calculating the cdf, since idk a smart way to figure all possible outcomes out
    from sympy import stats
    import re

    # Using the structure of the string to extract the rolled dice and result of rolling
    roll_input = roll_message.split("rolling ")[-1].split("\n")[0]
    roll_result = int(float(roll_message.split("=")[-1].split(" ")[0]))

    # Find the dice and the amount
    dice = []
    dice_faces = []
    # Finding the index for each time the letter d is used
    d_place = find_indexes(roll_input, 'd')
    modifiers = roll_input  # Used for finding modifiers

    # Go through every d to figure out what kind of roll it is
    for i in d_place:
        # If it's not a die roll, continue
        if not roll_input[i + 1].isdigit():
            continue
        # Find the amount of dice
        amount = 1
        for n in range(1, 4):  # check to see if there's more than one die
            try:
                if roll_input[i - n].isdigit():
                    amount = int(roll_input[i - n:i])
            except:
                break
        # Find the die type
        for n in range(1, 4):
            try:
                if roll_input[i + n].isdigit():
                    die = int(roll_input[i + 1:i + n + 1])
            except:
                break
        # Save the dice into the sympy die class
        for n in range(amount):
            dice.append(stats.Die(f'Die_{i}_{n + 1}', die))
            dice_faces.append(die)
        # remove the found dice from the modifiers string
        modifiers = modifiers.replace(f'd{die}', '')

    # Another shitty fix for now
    if len(dice_faces) >= 15:
        print("Too many dice")
        return

    # Find every case of "+ NUMBER" or "- NUMBER"
    modifiers1 = re.findall(r'[+\-*/] \d+', modifiers)
    modifiers2 = re.findall(r'[+\-*/]\d+', modifiers)

    # add the numbers together if there are any
    if len(modifiers1) != 0 or len(modifiers2) != 0:
        modifiers = eval(''.join(modifiers1)+''.join(modifiers2))
    else:
        modifiers = 0

    # Remove the modifier amount from the roll result
    roll_result = roll_result - modifiers

    mean = stats.E(sum(dice))

    # Check if the cdf is manageable
    print(dice_faces)
    pos_rolls = powerList(dice_faces)
    print(pos_rolls)
    if pos_rolls > 8100:
        return roll_input, roll_result + modifiers, mean + modifiers, "unavailable", "unavailable"

    # Using the density and keys function I can extract all possible outcomes
    pmf = stats.density(sum(dice))
    # Casting the values into ints so that I can use 'em
    if len(dice) == 1: # If there is only one die I cannot use keys
        possible_vals = range(1, die + 1)
    else:
        possible_vals = [int(k) for k in pmf.keys()]

    # Calculate the cdf by adding up all the pmfs
    cdf = 0
    for n in range(possible_vals.index(roll_result)):
        cdf += pmf[possible_vals[n]]
    #cdf = sum(pmf[0:possible_vals.index(roll_result)])

    return roll_input, roll_result + modifiers, mean+modifiers, pmf[roll_result], cdf


# Function used to figure out how hard it is to calculate
def powerList(myList):
    try:
        if len(myList) <= 1:
            return myList[0]
        # Take the power of elements one by one
        result = myList[0] ** (sum(myList[1:])/myList[0]+1)
        return result
    except:
        return 0


# A function for checking stat calls
def ret_input(driver, read_msgs, players, last_roll):
    from data import player_ids

    try:
        texts = WebDriverWait(driver, 5).until(
            EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="textchat"]//div[contains(text(),"--stats")]')))
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

        print20(driver, '(‎')
        print20(driver, f'**---------------------**')
        print20(driver, m_output)
        print20(driver, f'**---------------------**')


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