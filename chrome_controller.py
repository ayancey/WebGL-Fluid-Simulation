import threading
import time
from selenium import webdriver
from pyjoystick.sdl2 import Key, Joystick, run_event_loop
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--window-size=1000,1000")
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(options=options)

driver.get("http://localhost:63342/WebGL-Fluid-Simulation/index.html")
print(driver.title)


def print_add(joy):
    print('Added', joy)


def print_remove(joy):
    print('Removed', joy)


buttonPositionMap = {
    "H1": {
        "x": 1920 / 3840,
        "y": 37 / 2160,
        "x_delta": 0,
        "y_delta": 0.005,
        "handle": None,
        "pointer_id": None
    },
    "H4": {
        "x": 1920 / 3840,
        "y": 2125 / 2160,
        "x_delta": 0,
        "y_delta": -0.005,
        "handle": None,
        "pointer_id": None
    }
}

buttonKeyMap = {
    2: "H1",
    3: "H4"
}

last_pressed = time.time()


def key_received(key):
    global last_pressed
    if key.keytype == "Axis":
        return

    if key.number in buttonKeyMap:
        hex_pressed = buttonKeyMap[key.number]
        if key.value:
            ret_data = driver.execute_script(
                f"return startButtonIterAnimation(\"{hex_pressed}\", {buttonPositionMap[hex_pressed]['x']}, {buttonPositionMap[hex_pressed]['y']}, {buttonPositionMap[hex_pressed]['x_delta']}, {buttonPositionMap[hex_pressed]['y_delta']});")
            last_pressed = time.time()
            buttonPositionMap[hex_pressed]["handle"] = ret_data["handle"]
            buttonPositionMap[hex_pressed]["pointer_id"] = ret_data["pointer_id"]
        else:
            if buttonPositionMap[hex_pressed]["handle"]:
                driver.execute_script(f"clearInterval({buttonPositionMap[hex_pressed]['handle']});")
                driver.execute_script(
                    f"pointers.splice(pointers.findIndex(v => v.id === {buttonPositionMap[hex_pressed]['pointer_id']}), 1);")


def check_last_pressed():
    global last_pressed
    while True:
        if time.time() - last_pressed > 10:
            driver.execute_script(f"splatStack.push(parseInt(Math.random() * 20) + 5);")

        time.sleep(1)


threading.Thread(target=check_last_pressed).start()

run_event_loop(print_add, print_remove, key_received)
