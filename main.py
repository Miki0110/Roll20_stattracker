import os
import sys
import csv
import time
import ast
import atexit
import pandas as pd
import startUp
import playerClass as pc
import dice_calculations as dc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
from fractions import Fraction


# Defining a class for setting up the session
class Session:
    def __init__(self):
        self.driver = startUp.start_driver()  # Driver for controlling chrome
        startUp.loginRoll20(self.driver)  # Login to roll20

        self.last_roll = []  # Rolls and results seen during the session
        self.read_msgs = []  # Read message ids
        self.players = []  # Players objects made from data in data.py
        self.player_ids = []

        # Register the shutdown protocall
        atexit.register(lambda: self._exit_handler())

        # Load logs if any are there
        self.load_logs()

    # A function for checking stat calls
    def ret_input(self):

        # First check for messages that contain the ';;' input
        try:
            texts = self.driver.find_elements(By.XPATH, '//*[@id="textchat"]//div[contains(text(),";;")]')
        except Exception as es:
            a = es
            # This is just incase you go into a different roll 20 tab
            self.read_msgs = []
            return

        # At startup the already rolled rolls have to  be saved and skipped
        if len(self.read_msgs) == 0:
            for text in texts:
                self.read_msgs.append(str(text.get_attribute("data-messageid")))

        # Go through messages found
        for text in texts:
            m_id = str(text.get_attribute("data-messageid"))  # Message ID
            text_message = str(text.get_attribute("innerText")).lower()  # The actual message

            # Check if this message has been read before
            if m_id in self.read_msgs:
                continue
            # Save msg ID so it's skipped next time
            self.read_msgs.append(m_id)

            # By splitting the message between spaces a list of the commands are made
            command = text_message.split(';;')[-1].split(' ')  # eg. ';;stats last 3' = ['stats', 'last', '3']

            # Check for what kind of request it is
            # Help request
            if command[0] == 'help' or command[0] == 'h':
                m_output = '**Current requests**\n```;session {command}``*check rolls for the entire session*\n' \
                           '```;player {Player name} {command}``*check rolls of a single player*\n' \
                           '**Current commands**\n```;[request] last {number of rolls}``' \
                           ' *Returns the chance for a combined number of rolls*\n' \
                           '```;[request] stats`` *Returns the average and best rolls for the session*'

            # Session request
            elif command[0] == 'session' or command[0] == 's':
                if command[1] == 'last':
                    if len(command) > 2:
                        m_output = self._last_call(amount=int(command[2]))
                    else:
                        m_output = self._last_call()
                elif command[1] == 'stats':
                    m_output = self._stat_call()
                else:
                    print("Command not recognised")
                    return

            # Player request
            elif command[0] == 'player' or command[0] == 'p':
                player = self.players[int(self.player_ids.index(command[1]) / 2)]
                if command[2] == 'last':
                    if len(command) > 3:
                        m_output = self._last_call(player, amount=int(command[3]))
                    else:
                        m_output = self._last_call(player)
                elif command[2] == 'stats':
                    m_output = self._stat_call(player)
                else:
                    print("Command not recognised")
                    return
            else:
                print("Command not recognised")
                return

            # Print out the results found
            pc.print20(self.driver, '‎')
            pc.print20(self.driver, f'**--------------------**')
            pc.print20(self.driver, m_output)
            pc.print20(self.driver, f'**--------------------**')

    # Look for players in the session
    def find_players(self):
        # Find the player banners
        ps = self.driver.find_elements(By.XPATH, f'//*[@class="player ui-droppable ui-draggable"]')

        for p_bar in ps:
            # Get the player id from the banners
            p_id = p_bar.get_attribute("id").replace("player_", "")

            # Check if the person already has a class
            if p_id in self.player_ids:
                continue

            # retrieve the name of the ID
            p_name = p_bar.get_attribute("innerText").replace(u'\xa0\n', "").split(" ")[0]  # I only want the first name
            print(p_name)

            # Append the name and id into the session
            self.player_ids.append(str(p_name).lower())
            self.player_ids.append(p_id)

            # Create a player object for the person found
            self.players.append(pc.Player(p_name, p_id))

    # Function for checking every player individually
    def go_through_players(self):
        for i, player in enumerate(self.players):
            lr = player.check_roll(self.driver)
            if lr != 0 and lr is not None:
                self.last_roll.append(lr)

    # Function that returns the stats of a person or session
    def _stat_call(self, target=None, return_string=True):
        if target is None:
            best = [10, 10, 10, 'name']
            worst = [10, 10, 10, 'name']
            cdfs = []
            inv_cdfs = []

            for player in self.players:
                rolls, avg, w, b = player.curr_stats()
                if b == -1:  # incase the player has not rolled yet
                    continue
                cdfs.append(player.cdf)
                inv_cdfs.append(player.inv_cdf)

                # The worst seen rolls
                worst_roll, w_index = w
                if worst_roll < worst[0]:
                    worst = worst_roll, rolls[w_index * 2], rolls[w_index * 2 + 1], player.name

                # The best seen rolls
                best_roll, b_index = b
                if best_roll < best[0]:
                    best = best_roll, rolls[b_index * 2], rolls[b_index * 2 + 1], player.name

            # Since the lists of cdfs are inside one another I flatten the list out first
            cdfs = [item for sublist in cdfs for item in sublist]
            inv_cdfs = [item for sublist in inv_cdfs for item in sublist]

            avg_b = sum(inv_cdfs) / len(inv_cdfs) * 100

            # Write out the results
            m_output = f'\n**Session stats**\n' \
                       f'Rolls recorded = **{len(cdfs)}**\n' \
                       f'Average chance to roll that or higher = **{float(avg_b)}%**\n'\
                       f'Best roll was **"{best[1]} = {best[2]}"** '\
                       f'with a **{float(best[0] * 100)}%** chance, rolled by **{best[3]}**\n\n' \
                       f'Worst roll was **"{worst[1]} = {worst[2]}"** with a **{float(worst[0] * 100)}%** '\
                       f'chance, rolled by **{worst[3]}**'
            # If the function is used to just call stats
            if not return_string:
                return len(cdfs), float(avg_b), best, worst
            else:
                return m_output
        else:
            name = target.name
            rolls, avg, w, b = target.curr_stats()

            if b != -1:
                # The worst seen rolls
                worst_roll, w_index = w
                # The best seen rolls
                best_roll, b_index = b

                m_output = f'\n**Player {name}**\n' \
                           f'Rolls recorded = **{int(len(rolls)/2)}**\n' \
                           f'Average chance to roll that or higher = **{float(avg*100)}%**\n' \
                           f'Best roll **"{rolls[b_index * 2]} = {rolls[b_index * 2 + 1]}"** with a '\
                           f'**{float(best_roll * 100)}%** chance\n\n' \
                           f'Worst roll **"{rolls[w_index * 2]} = {rolls[w_index * 2 + 1]}"** with a '\
                           f'**{float(worst_roll * 100)}%** chance'
            else:
                m_output = f'Player {name} has not rolled yet'
            return m_output

    # Function that calculates and returns the last roll(s)
    def _last_call(self, target=None, amount=1):
        if target is None:
            rolls = []
            results = []
            modifiers = 0
            for i in range(amount):
                roll = self.last_roll[-(i+1)][0]
                res = self.last_roll[-(i+1)][1]
                dice, modifier = pc.ret_dice(roll)
                [rolls.append(int(die)) for die in dice]
                results.append(res-modifier)
                modifiers = modifiers+modifier
            output = dc.calc_dice(rolls, sum(results))
            if output != -1:

                m_output = f'\n**Last {amount} roll(s):**\nResulted in a total of = **{sum(results)+modifiers}**\n' \
                           f'Expected Value = **{float(output[0]+modifiers)}**\nWith a '\
                           f'**{(float(output[3]))*100}%** of rolling that or higher,' \
                           f' and a **{float(output[1])*100}%** chance for the exact value.'
            else:
                m_output = f'Too many dice to calculate'
        else:
            rolls = []
            results = []
            modifiers = 0
            for i in range(amount):
                roll = target.rolls[-(i*2+2)]
                res = target.rolls[-(i*2+1)]
                dice, modifier = pc.ret_dice(roll)
                [rolls.append(int(die)) for die in dice]
                results.append(res - modifier)
                modifiers = modifiers + modifier
            output = dc.calc_dice(rolls, sum(results))
            if output != -1:
                m_output = f'\n**Last {amount} roll(s):**\nResulted in a total of = **{sum(results) + modifiers}**\n' \
                           f'Expected Value = **{float(output[0] + modifiers)}**\nWith a '\
                           f'**{(float(output[3])) * 100}%** of rolling that or higher,' \
                           f' and a **{float(output[1]) * 100}%** chance for the exact value.'
            else:
                m_output = f'Too many dice to calculate'
        return m_output

    # Function for logging the stats of the session
    def log_session(self):
        # Get the date for the filename
        timestamp = time.strftime("%d-%m-%Y")
        filename = "Session_{}.csv".format(timestamp)
        with open(f'logs/{filename}', "w", newline="") as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            # Session sum-up
            header = ["Amount of rolls ", "Average roll chance ", "Best roll ", "Worst roll"]
            output = self._stat_call(return_string=False)
            # Write out the session
            writer.writerow(header)
            writer.writerow(output)

            # Individual player log
            header = ["Player", "ID", "Rolls", "CDF", "Inv CDF"]
            writer.writerow(header)
            for player in self.players:
                name = player.name
                pid = player.id
                rolls = player.rolls
                cdf = player.cdf
                inv_cdf = player.inv_cdf
                writer.writerow([name, pid, rolls, cdf, inv_cdf])

    # Function for loading logs
    def load_logs(self):
        # Check if there already is a log file
        folder_path = os.path.join(os.getcwd(), "logs")
        log_files = os.listdir(folder_path)
        timestamp = time.strftime("%d-%m-%Y")
        filename = "Session_{}.csv".format(timestamp)
        # If there are none we simply return doing nothing
        if filename not in log_files:
            return
        # In case there is a file but it is empty
        if os.path.getsize(f'logs/{filename}') == 0:
            return

        print('Found previous session, loading the previous rolls into this session...')
        # Load the file in
        df = pd.read_csv(f'logs/{filename}', header=2)
        # Extract the data, and evaluate those that include numbers
        player_ids = df['ID'].values
        names = df['Player'].values
        rolls = df['Rolls'].apply(ast.literal_eval).values
        cdfs = df['CDF'].values
        cdfs = [eval(values) for values in cdfs]
        inv_cdfs = df['Inv CDF'].values
        inv_cdfs = [eval(values) for values in inv_cdfs]
        for i, ids in enumerate(player_ids):
            if ids in self.player_ids:
                player = self.players[int(self.player_ids.index(ids) / 2)]
            else:
                # Create a player object for the person found
                self.players.append(pc.Player(names[i], ids))
                self.player_ids.append(str(names[i]).lower())
                self.player_ids.append(ids)

                player = self.players[-1]
            for j in range(len(rolls[i])):
                player.rolls.append(rolls[i][j])
            for j in range(len(cdfs[i])):
                player.cdf.append(cdfs[i][j])
                player.inv_cdf.append(inv_cdfs[i][j])
        return

    # Function used to guarantee the Chromedriver is closed
    def _exit_handler(self):
        print("Closing down the Chromedriver")
        if len(self.last_roll) >= 1:
            print("Saving logs...")
            self.log_session()
        self.driver.quit()


# MAIN LOOP
if __name__ == "__main__":
    session = Session()  # Initiate a session
    while True:
        try:
            session.find_players()  # Find players and their ID
            session.go_through_players()  # check for rolls
            session.ret_input()  # check for commands

        # Go through exceptions, and act accordingly
        except NoSuchWindowException as e:  # In case the browser window is closed
            print("The browser has been closed")
            # Check if the browser has been closed
            try:
                session.driver.quit()
            except Exception as e:
                pass
            # Exit the program
            sys.exit()

        except WebDriverException as e:  # Sometimes Selenium cannot find a specified object (This is generally ignored)
            print("An error occurred while interacting with the browser")
        except Exception as e:  # In case an exception occurs due to bugs or errors in the code
            print("Unknown error occurred:", e)
