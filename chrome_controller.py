import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from colour import Color
import pygame
import sys
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
import datetime

options = Options()
options.add_argument("--window-size=1000,1031")
options.add_argument("--app=http://localhost:8000")
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(options=options)

driver.get("http://localhost:8000")
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
    pygame.K_1: "H1",
    pygame.K_2: "H2",
    pygame.K_3: "H3",
    pygame.K_4: "H4",
    pygame.K_5: "H5",
    pygame.K_6: "H6"
}
last_pressed = time.time()

idle = False

total_button_presses = 0
total_unidle_transition = 0


def key_received(key):
    global last_pressed
    global idle
    global total_button_presses
    global total_unidle_transition

    if event.type not in [pygame.KEYDOWN, pygame.KEYUP]:
        return

    # Press m for menu toggle (hidden by default)
    if key.key == 109:
        if event.type == pygame.KEYUP:
            driver.execute_script("toggle_config();")

    if key.key in buttonKeyMap:
        last_pressed = time.time()

        if idle:
            # Massively raise density dissipation for 250ms to clear the screen quickly
            driver.execute_script(
                "config.DENSITY_DISSIPATION = 10;setTimeout(function(){config.DENSITY_DISSIPATION = 0.7;}, 250);")
            idle = False
            total_unidle_transition += 1

        hex_pressed = buttonKeyMap[key.key]
        if event.type == pygame.KEYDOWN:
            total_button_presses += 1

            # Velocity goes up if the button is pressed repeatedly
            x_delta = buttonPositionMap[hex_pressed]['x_delta']
            y_delta = buttonPositionMap[hex_pressed]['y_delta']

            r, g, b = buttonPositionMap[hex_pressed]["color"].rgb

            ret_data = driver.execute_script(
                f"return startButtonIterAnimation(\"{hex_pressed}\", {buttonPositionMap[hex_pressed]['x']}, {buttonPositionMap[hex_pressed]['y']}, {x_delta}, {y_delta}, {{r:{r},g:{g},b:{b}}});")

            buttonPositionMap[hex_pressed]["handle"] = ret_data["handle"]
            buttonPositionMap[hex_pressed]["pointer_id"] = ret_data["pointer_id"]
        elif event.type == pygame.KEYUP:
            if buttonPositionMap[hex_pressed]["handle"]:
                driver.execute_script(
                    f"setTimeout(function(){{clearInterval({buttonPositionMap[hex_pressed]['handle']});pointers.splice(pointers.findIndex(v => v.id === {buttonPositionMap[hex_pressed]['pointer_id']}), 1);}}, 250);")


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


def log_interacts():
    while True:
        try:
            with open("interaction_log.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.datetime.now(datetime.timezone.utc).isoformat()} - presses:{total_button_presses},transitions:{total_unidle_transition}\n")
        except:
            print("log write failed")
        time.sleep(300)


threading.Thread(target=log_interacts).start()


def config_handler(addr, val):
    driver.execute_script(f"config.{addr.split('/')[-1]} = {val};")
    print(f"changed {addr.split('/')[-1]} to {val}")


dispatcher = Dispatcher()
dispatcher.map("/config/*", config_handler)

server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", 6420), dispatcher)
print("Serving on {}".format(server.server_address))

threading.Thread(target=server.serve_forever).start()

# Initialize Pygame
pygame.init()

# Set up display
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("GigaHex Keyboard Control (MUST BE FOCUSED)")

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        key_received(event)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
