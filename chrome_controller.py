import threading
import time
from selenium import webdriver
from pyjoystick.sdl2 import Key, Joystick, run_event_loop
from selenium.webdriver.chrome.options import Options
from colour import Color

options = Options()
options.add_argument("--window-size=1000,1031")
options.add_argument("--app=http://localhost:63342/WebGL-Fluid-Simulation/index.html")
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
        "x": 0.5,
        "y": 0,
        "x_delta": 0,
        "y_delta": 0.005,
        "handle": None,
        "pointer_id": None,
        "color": Color("yellow")
    },
    "H2": {
        "x": 0.93,
        "y": 0.25,
        "x_delta": -0.005,
        "y_delta": 0.0029,
        "handle": None,
        "pointer_id": None,
        "color": Color("orangered")
    },
    "H3": {
        "x": 0.93,
        "y": 0.75,
        "x_delta": -0.005,
        "y_delta": -0.0029,
        "handle": None,
        "pointer_id": None,
        "color": Color("red")
    },
    "H4": {
        "x": 0.5,
        "y": 1,
        "x_delta": 0,
        "y_delta": -0.005,
        "handle": None,
        "pointer_id": None,
        "color": Color("purple")
    },
    "H5": {
        "x": 0.07,
        "y": 0.75,
        "x_delta": 0.005,
        "y_delta": -0.0029,
        "handle": None,
        "pointer_id": None,
        "color": Color("blue")
    },
    "H6": {
        "x": 0.07,
        "y": 0.25,
        "x_delta": 0.005,
        "y_delta": 0.0029,
        "handle": None,
        "pointer_id": None,
        "color": Color("green")
    }
}

buttonKeyMap = {
    3: "H1",
    4: "H2",
    5: "H3",
    6: "H4",
    7: "H5",
    2: "H6"
}

last_pressed = time.time()

idle = False


def key_received(key):
    global last_pressed
    global idle
    if key.keytype == "Axis":
        return

    if key.number in buttonKeyMap:
        last_pressed = time.time()

        if idle:
            driver.execute_script("config.DENSITY_DISSIPATION = 10;setTimeout(function(){config.DENSITY_DISSIPATION = 0.7;}, 1000);")
            idle = False

        hex_pressed = buttonKeyMap[key.number]
        if key.value:
            # Velocity goes up if the button is pressed repeatedly
            x_delta = buttonPositionMap[hex_pressed]['x_delta']
            y_delta = buttonPositionMap[hex_pressed]['y_delta']

            r, g, b = buttonPositionMap[hex_pressed]["color"].rgb

            ret_data = driver.execute_script(
                f"return startButtonIterAnimation(\"{hex_pressed}\", {buttonPositionMap[hex_pressed]['x']}, {buttonPositionMap[hex_pressed]['y']}, {x_delta}, {y_delta}, {{r:{r},g:{g},b:{b}}});")

            buttonPositionMap[hex_pressed]["handle"] = ret_data["handle"]
            buttonPositionMap[hex_pressed]["pointer_id"] = ret_data["pointer_id"]
        else:
            if buttonPositionMap[hex_pressed]["handle"]:
                driver.execute_script(f"setTimeout(function(){{clearInterval({buttonPositionMap[hex_pressed]['handle']});pointers.splice(pointers.findIndex(v => v.id === {buttonPositionMap[hex_pressed]['pointer_id']}), 1);}}, 250);")




def check_last_pressed():
    global last_pressed
    global idle
    while True:
        # If button hasn't been pressed in 10 seconds, make random splats and reset the speed
        if time.time() - last_pressed > 10:
            driver.execute_script(f"splatStack.push(parseInt(Math.random() * 20) + 5);")
            idle = True

        time.sleep(1)


threading.Thread(target=check_last_pressed).start()

run_event_loop(print_add, print_remove, key_received)
