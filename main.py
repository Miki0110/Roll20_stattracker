import startUp
import playerClass as pc
import dice_calculations as dc
from selenium.webdriver.common.by import By


# Defining a class for setting up the session
class Session:
    def __init__(self):
        self.driver = startUp.start_driver()  # Driver for controlling chrome
        startUp.loginRoll20(self.driver) # Login to roll20

        self.last_roll = []  # Rolls and results seen during the session
        self.read_msgs = []  # Read message ids
        self.players = []  # Players objects made from data in data.py
        self.player_ids = []

    # A function for checking stat calls
    def ret_input(self):

        # First check for messages that contain the ';;' input
        try:
            texts = self.driver.find_elements(By.XPATH, '//*[@id="textchat"]//div[contains(text(),";;")]')
        except:
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
            if command[0] == 'help'or command[0] == 'h':
                m_output = '**Current requests**\n```;session {command}``*check rolls for the entire session*\n' \
                           '```;player {Player name} {command}``*check rolls of a single player*\n' \
                           '**Current commands**\n```;{request} last {number of rolls}``' \
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
    def _stat_call(self, target=None):
        if target is None:
            best = [0,0,0,'name']
            cdfs = []
            for player in self.players:
                rolls, _, best_roll, b_index = player.curr_stats()
                if b_index == -1: #  incase the player has not rolled yet
                    continue
                cdfs.append(player.cdfs)
                if best_roll > best[0]:
                    best = best_roll, rolls[b_index * 2], rolls[b_index * 2 + 1], player.name
            # Since the lists of cdfs are inside one another I flatten the list out first
            cdfs = [item for sublist in cdfs for item in sublist]
            avg = sum(cdfs) / len(cdfs)

            # Write out the results
            m_output = f'\n**Session stats**\nRolls recorded = **{len(cdfs)}**\nAverage roll chance (1-cdf) = **{float(1 - avg)}**\nBest roll was **"{best[1]}' \
                       f' = {best[2]}"** with a **{float((1 - best[0]) * 100)}%** chance, rolled by **{best[3]}**'
            return m_output
        else:
            name = target.name
            rolls, avg_roll, best_roll, b_index = target.curr_stats()
            if b_index != -1:
                m_output = f'\n**Player {name}**\nRolls recorded = **{len(rolls)}**\nAverage roll chance (1-cdf) = **{float(1 - avg_roll)}**\nBest roll **"{rolls[b_index * 2]}' \
                           f' = {rolls[b_index * 2 + 1]}"** with a **{float((1 - best_roll) * 100)}%** chance'
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
                           f'Expected Value = **{float(output[0]+modifiers)}**\nWith a **{(1-float(output[2]))*100}%** of rolling that or higher,' \
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
                           f'Expected Value = **{float(output[0] + modifiers)}**\nWith a **{(1 - float(output[2])) * 100}%** of rolling that or higher,' \
                           f' and a **{float(output[1]) * 100}%** chance for the exact value.'
            else:
                m_output = f'Too many dice to calculate'
        return m_output


def main():
    session = Session()  # Initiate a session
    while True:
        try:
            session.find_players()  # Find players and their ID
            session.go_through_players()  # check for rolls
            session.ret_input()  # check for commands
        except Exception as e:
            # Sometimes the selenium makes errors, print them out if that's the case
            print(e)


if __name__ == "__main__":
    main()
