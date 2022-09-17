import playerClass as func
import startUp


# Function to loop through each player defined
def go_through_players(driver, players):
    for player in players:
        rolldata = player.check_roll(driver)

    return rolldata


# Function for checking for commands
def check_commands(driver, players, last_roll):
    func.ret_input(driver, read_msgs, players, last_roll)


def main():
    driver = startUp.start_driver()
    players = startUp.loginRoll20(driver)

    global read_msgs

    last_roll = 0,0,0
    read_msgs = []

    print("start")
    while True:
        try:
            roll_data = go_through_players(driver, players)
            if roll_data != None:
                last_roll = roll_data
            check_commands(driver, players, last_roll)
        except Exception as e:
            print(e)
            read_msgs = []


if __name__ == "__main__":
    main()
