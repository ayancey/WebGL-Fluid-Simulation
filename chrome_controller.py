import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from colour import Color
import pygame
import sys

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
    pygame.K_1: "H1",
    pygame.K_2: "H2",
    pygame.K_3: "H3",
    pygame.K_4: "H4",
    pygame.K_5: "H5",
    pygame.K_6: "H6"
}

last_pressed = time.time()

idle = False


def key_received(key):
    global last_pressed
    global idle

    if event.type not in [pygame.KEYDOWN, pygame.KEYUP]:
        return

    if key.key in buttonKeyMap:
        last_pressed = time.time()

        if idle:
            driver.execute_script("config.DENSITY_DISSIPATION = 10;setTimeout(function(){config.DENSITY_DISSIPATION = 0.7;}, 250);")
            idle = False

        hex_pressed = buttonKeyMap[key.key]
        if event.type == pygame.KEYDOWN:
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



# Initialize Pygame
pygame.init()

# Set up display
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pygame Key Input Example")

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        key_received(event)

        # Check for key presses
        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_1:
        #         print("Number 1 key pressed")
        #     elif event.key == pygame.K_2:
        #         print("Number 2 key pressed")
        #     elif event.key == pygame.K_3:
        #         print("Number 3 key pressed")
        #     elif event.key == pygame.K_4:
        #         print("Number 4 key pressed")
        #     elif event.key == pygame.K_5:
        #         print("Number 5 key pressed")
        #     elif event.key == pygame.K_6:
        #         print("Number 6 key pressed")

    # Fill the screen with a color (optional)
    #screen.fill((0, 0, 0))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()


#run_event_loop(print_add, print_remove, key_received)
