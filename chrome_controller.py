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


key_6_handle = 0
key_5_handle = 0


def key_received(key):
    global key_6_handle
    global key_5_handle

    # Only care about button down
    if key.value == 1:
        if key.number == 6:
            print("key 6 pressed")
            key_6_handle = driver.execute_script("return startButton(6, h1_x, h1_y);")
            print(key_6_handle)
        elif key.number == 5:
            print("key 5 pressed")
            key_5_handle = driver.execute_script("return startButton(5, h4_x, h4_y);")
        else:
            print("unknown button pressed")
    elif key.value == 0:
        if key.number == 6:
            if key_6_handle != 0:
                driver.execute_script(f"clearInterval({key_6_handle});")
        elif key.number == 5:
            if key_5_handle != 0:
                driver.execute_script(f"clearInterval({key_5_handle});")
    else:
        print("what is this shit")


run_event_loop(print_add, print_remove, key_received)
