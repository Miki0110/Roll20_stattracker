from selenium import webdriver
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
def startup(driver):
    from data import login_password, login_email
    #Open the website
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


# Function used to close down the Chromedriver
def exit_handler(driver):
    print("Closing down the Chromedriver")
    driver.quit()


# Function used to retrieve stats when the session ends
def stat_handler(player):
    player.ret_stats()


# Simpel index list function
def find_indexes(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]


# function for retrieving the dice rolls
def ret_stats(roll_message):
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
def ret_input(driver, read_msgs, players):
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
        while True:
            try:
                m_id = str(text.get_attribute("data-messageid"))
                break
            except:
                pass
        text_message = str(text.get_attribute("innerText"))

        # Check if this message has been read before
        if m_id in read_msgs:
            continue

        read_msgs.append(m_id)

        target_p = text_message.split("--stats ")[-1]
        p_index = int(player_ids.index(target_p)/2)

        rolls, avg_roll, best_roll, b_index = players[p_index].ret_stats()
        if b_index != -1:
            m_output = f'Player {target_p}\nAverage roll chance (1-cdf) = {float(1-avg_roll)}\nBest roll "{rolls[b_index*2]}' \
                       f' = {rolls[b_index*2+1]}" with a {float((1-best_roll)*100)}% chance'
        else:
            m_output = f'Player {target_p} has not rolled yet'

        text_area = driver.find_element(By.XPATH, '// *[ @ id = "textchat-input"] / textarea')
        text_area.send_keys(m_output)
        text_area.send_keys(Keys.ENTER)