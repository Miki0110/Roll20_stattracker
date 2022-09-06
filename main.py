import playerClass as func
import startUp


# Function to loop through each player defined
def go_through_players(driver, players):
    for player in players:
        player.check_roll(driver)
    # Check for command inputs
    func.ret_input(driver, read_msgs, players)


def main():
    driver = startUp.start_driver()
    players = startUp.loginRoll20(driver)

    global read_msgs
    read_msgs = []

    print("start")
    while True:
        try:
            go_through_players(driver, players)
        except:
            print('error')
        #    read_msgs = []


if __name__ == "__main__":
    main()