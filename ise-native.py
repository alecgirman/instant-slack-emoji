import subprocess
import pyautogui
from os import system
from time import sleep
from sys import argv
from uuid import uuid4


def run_proc(command: str) -> str:
    args = command.split(" ")  # turn command into array
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode, result.stdout.decode("utf-8")


# check xclip dependency
if run_proc("which xclip")[0] != 0:
    print("xclip not found!  Please install xclip in order for this to work.")
    print("\tUbuntu/Debian: sudo apt install xclip")
    print("\tArch: pacman -S xclip")

if "image/png" in run_proc("xclip -selection clipboard -t TARGETS -o")[1]:
    filepath = f"/tmp/{uuid4()}.png"
    system(f"xclip -selection clipboard -t image/png -o > {filepath}")

    name = argv[1]
    system("slack")
    sleep(0.25)

    # open chat with slackbot
    pyautogui.hotkey("ctrl", "t")
    pyautogui.write("slackbot", interval=0.1)
    sleep(5)
    pyautogui.press("enter")

    # get to emoji panel via reaction
    pyautogui.press("up")
    pyautogui.press("r")

    # select 'add emoji'
    pyautogui.press("tab", presses=6)
    pyautogui.press("enter")

    # select upload emoji
    sleep(0.1)
    pyautogui.press("tab", presses=2)
    pyautogui.press("enter")

    # input filename
    pyautogui.write(filepath)
    pyautogui.press("enter")
    sleep(1)

    pyautogui.press("tab")
    pyautogui.write(name, interval=0.05)

    # save
    pyautogui.press("tab", presses=2)
    pyautogui.press("enter")
