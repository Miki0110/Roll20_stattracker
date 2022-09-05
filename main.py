import open_login as func
from data import player_ids
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
            roll_inp, result, mean, pmf, cdf = func.ret_stats(roll_message)  # Retrieve the statistical values
            if cdf != 'unavailable':
                print(f'Player {self.name} rolls\nMean = {float(mean)}\npmf = {float(pmf)}\ncdf = {float(1 - cdf)}')
                self.cdfs.append(cdf)
                self.rolls.append(roll_inp)
                self.rolls.append(result)
            else:  # If the message contains too many dice, the cdf and pdf will be skipped
                print(f'Player {self.name} rolls\nMean = {float(mean)}')

    # Retrieve data from the object
    def ret_stats(self):  # Returns (rolls, average roll, best roll, best roll index)
        if len(self.cdfs) == 0:
            return ['no rolls', 'no rolls', 'no rolls', -1]
        avg_roll = sum(self.cdfs) / len(self.cdfs)
        best_roll = max(self.cdfs)
        b_index = self.cdfs.index(best_roll)
        return self.rolls, avg_roll, best_roll, b_index


# Function to loop through each player defined
def go_through_players(driver, players):
    for player in players:
        player.check_roll(driver)
    # Check for command inputs
    func.ret_input(driver, read_msgs, players)


def main():
    driver = func.start_driver()
    func.startup(driver)
    players = []
    for i in range(int(len(player_ids)/2)):
        players.append(Player(player_ids[int(i*2)], player_ids[int(i*2)+1]))

    global read_msgs
    read_msgs = []

    print("start")
    while True:
        try:
            go_through_players(driver, players)
        except:
            print('error')
            read_msgs = []


if __name__ == "__main__":
    main()