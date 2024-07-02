import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from colour import Color
import pygame
import sys
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
import math


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
    "h1": "H1",
    "h2": "H2",
    "h3": "H3",
    "h4": "H4",
    "h5": "H5",
    "h6": "H6"
}
last_pressed = time.time()

idle = False


def key_received(unused_addr, pressed):
    global last_pressed
    global idle

    # if event.type not in [pygame.KEYDOWN, pygame.KEYUP]:
    #     return
    print((unused_addr, pressed))

    key = unused_addr.split("/")[-1]

    if key in buttonKeyMap:
        last_pressed = time.time()

        if idle:
            driver.execute_script("config.DENSITY_DISSIPATION = 10;setTimeout(function(){config.DENSITY_DISSIPATION = 0.7;}, 250);")
            idle = False

        hex_pressed = buttonKeyMap[key]
        if pressed:
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


def print_volume_handler(unused_addr, args, volume):
  print("[{0}] ~ {1}".format(args[0], volume))


def print_compute_handler(unused_addr, args, volume):
  try:
    print("[{0}] ~ {1}".format(args[0], args[1](volume)))
  except ValueError: pass


def vorticity_handler(unused_addr, vort):
    print(f"changed vorticity to {vort}")
    driver.execute_script(f"config.CURL = {vort};")


dispatcher = Dispatcher()
dispatcher.map("/filter", print)
dispatcher.map("/button/*", key_received)
dispatcher.map("/vorticity", vorticity_handler)
dispatcher.map("/logvolume", print_compute_handler, "Log volume", math.log)

server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", 6420), dispatcher)
print("Serving on {}".format(server.server_address))
server.serve_forever()


# Initialize Pygame
# pygame.init()
#
# # Set up display
# width, height = 640, 480
# screen = pygame.display.set_mode((width, height))
# pygame.display.set_caption("Pygame Key Input Example")
#
# # Main loop
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#
#         key_received(event)
#
#         # Check for key presses
#         # if event.type == pygame.KEYDOWN:
#         #     if event.key == pygame.K_1:
#         #         print("Number 1 key pressed")
#         #     elif event.key == pygame.K_2:
#         #         print("Number 2 key pressed")
#         #     elif event.key == pygame.K_3:
#         #         print("Number 3 key pressed")
#         #     elif event.key == pygame.K_4:
#         #         print("Number 4 key pressed")
#         #     elif event.key == pygame.K_5:
#         #         print("Number 5 key pressed")
#         #     elif event.key == pygame.K_6:
#         #         print("Number 6 key pressed")
#
#     # Fill the screen with a color (optional)
#     #screen.fill((0, 0, 0))
#
#     # Update the display
#     pygame.display.flip()
#
# # Quit Pygame
# pygame.quit()
# sys.exit()


#run_event_loop(print_add, print_remove, key_received)
