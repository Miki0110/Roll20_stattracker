import startUp
import dice_calculations as dc
from selenium.webdriver.common.by import By
import playerClass as func


class Session():
    def __init__(self):
        self.driver = startUp.start_driver()
        self.last_roll = []
        self.read_msgs = []
        self.players = startUp.loginRoll20(self.driver)

    # A function for checking stat calls
    def ret_input(self):
        from data import player_ids

        try:
            texts = self.driver.find_elements(By.XPATH, '//*[@id="textchat"]//div[contains(text(),";;")]')
        except:
            self.read_msgs = []
            return

        if len(self.read_msgs) == 0:
            for text in texts:
                self.read_msgs.append(str(text.get_attribute("data-messageid")))

        for text in texts:
            m_id = str(text.get_attribute("data-messageid"))
            text_message = str(text.get_attribute("innerText"))

            # Check if this message has been read before
            if m_id in self.read_msgs:
                continue
            # Save msg ID so it's skipped next time
            self.read_msgs.append(m_id)

            command = text_message.split(';;')[-1].split(' ')

            if command[0] == 'help'or command[0] == 'h':
                m_output = '**Current requests**\n```;session {command}``*check rolls for the entire session*\n' \
                           '```;player {Player name} {command}``*check rolls of a single player*\n' \
                           '**Current commands**\n```;{request} last {number of rolls}``' \
                           ' *Returns the chance for a combined number of rolls*\n' \
                           '```;[request] stats`` *Returns the average and best rolls for the session*'

            elif command[0] == 'session' or command[0] == 's':
                if command[1] == 'last':
                    if len(command) > 2:
                        m_output = self.last_call(amount=int(command[2]))
                    else:
                        m_output = self.last_call()
                elif command[1] == 'stats':
                    m_output = self.stat_call()
                else:
                    print("Command not recognised")
                    return

            elif command[0] == 'player' or command[0] == 'p':
                player = self.players[int(player_ids.index(command[1]) / 2)]
                if command[2] == 'last':
                    if len(command) > 3:
                        m_output = self.last_call(player, amount=int(command[3]))
                    else:
                        m_output = self.last_call(player)
                elif command[2] == 'stats':
                    m_output = self.stat_call(player)
                else:
                    print("Command not recognised")
                    return
            else:
                print("Command not recognised")
                return

            func.print20(self.driver, '‎')
            func.print20(self.driver, f'**--------------------**')
            func.print20(self.driver, m_output)
            func.print20(self.driver, f'**--------------------**')

    def go_through_players(self):
        for i, player in enumerate(self.players):
            lr = player.check_roll(self.driver)
            if lr != 0 and lr is not None:
                self.last_roll.append(lr)

    def stat_call(self, target=None):
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
            avg = sum(cdfs) / len(cdfs)
            m_output = f'\n**Session stats**\nAverage roll chance (1-cdf) = **{float(1 - avg)}**\nBest roll was **"{best[1]}' \
                       f' = {best[2]}"** with a **{float((1 - best[0]) * 100)}%** chance, rolled by **{best[3]}**'
            return m_output
        else:
            name = target.name
            rolls, avg_roll, best_roll, b_index = target.curr_stats()
            if b_index != -1:
                m_output = f'\n**Player {name}**\nAverage roll chance (1-cdf) = **{float(1 - avg_roll)}**\nBest roll **"{rolls[b_index * 2]}' \
                           f' = {rolls[b_index * 2 + 1]}"** with a **{float((1 - best_roll) * 100)}%** chance'
            else:
                m_output = f'Player {name} has not rolled yet'
            return m_output

    def last_call(self, target=None, amount=1):
        if target is None:
            rolls = []
            results = []
            modifiers = 0
            for i in range(amount):
                roll = self.last_roll[-(i+1)][0]
                res = self.last_roll[-(i+1)][1]
                dice, modifier = func.ret_dice(roll)
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
                dice, modifier = func.ret_dice(roll)
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


session = Session()
while True:
    session.go_through_players()
    session.ret_input()
