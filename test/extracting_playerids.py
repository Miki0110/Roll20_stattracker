import startUp
from selenium.webdriver.common.by import By

def find_players():
    #<div class="player ui-droppable ui-draggable" id="player_-MeYzDW63pHnEnovXXkW"><div class="deckhands"></div><div class="video player-bookmark ui-draggable" style="background-image: url(/users/avatar/8406256/150);"><div data-fm-webrtc-inner-container="true" style="position: relative; width: 100%; height: 100%;"></div></div><div class="pause-video-icon"><span class="webrtc-icon webrtc-video-show"></span></div><div class="muted-self-icon"><span class="webrtc-icon webrtc-audio-unmute"></span></div><div class="muted-other-icon"><span class="webrtc-icon webrtc-audio-unmute"></span></div><div class="in-my-whisper-icon"><span class="webrtc-icon webrtc-whisper"></span></div><div class="connection-status-indicators"><div class="connection-status-connecting pictos">0</div><div class="connection-status-failed pictos">!</div></div><input class="playercolor colorpicker" data-offsetleft="-15" data-offsettop="-450" type="text" style="display: none;"><div class="color_picker" style="background-image: none; background-color: rgb(121, 211, 248);">&nbsp;</div><div class="playername player-bookmark ui-draggable"><div class="volume-meter"></div><span class="name">Miki P.</span></div><span class="player-handle"></span></div>
    try:
        #'//*[@id="textchat"]//div[contains(text(),"--stats")]'
        players = driver.find_elements(By.XPATH, f'//*[@class="player ui-droppable ui-draggable"]')
    except Exception as e:
        print(e)
        return 0

    for p_bar in players:
        p_id = p_bar.get_attribute("id")
        p_id = p_id.replace("player_", "")

        if p_id in ps:
            continue

        p_name = p_bar.get_attribute("outerText")

        print(f'name = {p_name}\nid={p_id}')
        ps.append(p_id)

driver = startUp.start_driver()
startUp.loginRoll20(driver)

ps = []

while True:
    find_players()
    print(ps)
