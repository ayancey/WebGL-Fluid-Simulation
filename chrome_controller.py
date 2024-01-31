import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyjoystick.sdl2 import Key, Joystick, run_event_loop
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder



options = Options()
options.add_argument("--window-size=1000,1000")

driver = webdriver.Chrome(options=options)


driver.get("http://localhost:63342/WebGL-Fluid-Simulation/index.html")
print(driver.title)
# search_bar = driver.find_element_by_name("q")
# search_bar.clear()
# search_bar.send_keys("getting started with python")
# search_bar.send_keys(Keys.RETURN)
# print(driver.current_url)
# driver.close()




def print_add(joy):
    print('Added', joy)


def print_remove(joy):
    print('Removed', joy)


def key_received(key):
    # Only care about button down
    if key.value == 1:
        if key.number == 6:
            print("key 6 pressed")
            driver.execute_script("runLoop(h1_x, h1_y, 0, 0.01);")
            # send_osc_value("/composition/layers/2/clips/1/connect", 1)
        elif key.number == 5:
            print("key 5 pressed")
            driver.execute_script("runLoop(h4_x, h4_y, 0, -0.01);")
            # send_osc_value("/composition/layers/2/clips/2/connect", 1)
        else:
            print("unknown button pressed")


run_event_loop(print_add, print_remove, key_received)
