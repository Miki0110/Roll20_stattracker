import open_login as func
from data import player_ids
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



class Player:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.read_msg = []
        self.rolls = []
        self.cdfs = []

    def check_roll(self, driver):
        #print(f'//div[@class="message rollresult you player-{self.id} quantumRoll"]')
        try:
            rolls = WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located(
                (By.XPATH, f'//div[@class="message rollresult you player-{self.id} quantumRoll"]')))
        except:
            return

        if len(self.read_msg) == 0:
            for roll in rolls:
                self.read_msg.append(str(roll.get_attribute("data-messageid")))

        for roll in rolls:
            m_id = str(roll.get_attribute("data-messageid"))
            roll_message = str(roll.get_attribute("outerText"))

            # Check if this message has been read before
            if m_id in self.read_msg:
                continue
            # Save the message as read
            self.read_msg.append(m_id)

            # Go through the actual values of the dice
            print("calculating...")
            roll_inp, result, mean, pmf, cdf = func.ret_stats(roll_message)
            if cdf != 'unavailable':
                print(f'Player {self.name} rolls\nMean = {float(mean)}\npmf = {float(pmf)}\ncdf = {float(1 - cdf)}')
                self.cdfs.append(cdf)
                self.rolls.append(roll_inp)
                self.rolls.append(result)
            else:
                print(f'Player {self.name} rolls\nMean = {float(mean)}')



    def ret_stats(self):
            avg_roll = sum(self.cdfs) / len(self.cdfs)
            best_roll = max(self.cdfs)
            b_index = self.cdfs.index(best_roll)
            return self.rolls, avg_roll, best_roll, b_index
            #print(f'Player {self.name}\nAverage roll chance = {avg_roll}\nBest roll "{self.rolls[b_index*2]}'
            #      f' = {self.rolls[b_index*2+1]}" with a {best_roll*100}% chance')


def go_through_players(driver, players):
    for player in players:
        player.check_roll(driver)
    func.ret_input(driver, read_msgs, players)


driver = func.start_driver()
func.startup(driver)
players = []
for i in range(int(len(player_ids)/2)):
    players.append(Player(player_ids[int(i*2)], player_ids[int(i*2)+1]))

global read_msgs
read_msgs = []

print("start")
while True:
    go_through_players(driver, players)