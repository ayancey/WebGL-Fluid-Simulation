import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from colour import Color
import serial

button_state_map = {
    "H1": "UP",
    "H2": "UP",
    "H3": "UP",
    "H4": "UP",
    "H5": "UP",
    "H6": "UP"
}


# Function to handle incoming serial data


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
        "color": Color("orange")
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

buttonPPSMap = {
    "H1": 1,
    "H2": 1,
    "H3": 1,
    "H4": 1,
    "H5": 1,
    "H6": 1
}

last_pressed = time.time()


def key_received(key, state):
    global last_pressed

    hex_pressed = key

    if state:
        x_delta = buttonPositionMap[hex_pressed]['x_delta'] * buttonPPSMap[hex_pressed]
        y_delta = buttonPositionMap[hex_pressed]['y_delta'] * buttonPPSMap[hex_pressed]

        r, g, b = buttonPositionMap[hex_pressed]["color"].rgb


        ret_data = driver.execute_script(
            f"return startButtonIterAnimation(\"{hex_pressed}\", {buttonPositionMap[hex_pressed]['x']}, {buttonPositionMap[hex_pressed]['y']}, {x_delta}, {y_delta}, {{r:{r},g:{g},b:{b}}});")
        last_pressed = time.time()
        buttonPositionMap[hex_pressed]["handle"] = ret_data["handle"]
        buttonPositionMap[hex_pressed]["pointer_id"] = ret_data["pointer_id"]
        buttonPPSMap[hex_pressed] += 1
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

        for hexa in buttonPPSMap:
            if buttonPPSMap[hexa] > 1:
                buttonPPSMap[hexa] -= 1

        time.sleep(1)

        print(buttonPPSMap)


threading.Thread(target=check_last_pressed).start()


def serial_listener(serial_port):
    with serial.Serial(serial_port, 115200) as ser:
        while True:
            line = ser.readline().decode('utf-8').strip()

            hexa = line.split("_")[0]
            state = line.split("_")[1]

            if hexa in button_state_map:
                if state != button_state_map[hexa]:
                    print(f"Changed: {line}")
                    if state == "UP":
                        key_received(hexa, False)
                    elif state == "DOWN":
                        key_received(hexa, True)

                    button_state_map[hexa] = state


serial_listener("COM4")
