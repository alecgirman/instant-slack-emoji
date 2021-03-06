from uuid import uuid4
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pyautogui

from dotenv import load_dotenv
from envs import env
from time import sleep
from os import system
from sys import argv


load_dotenv()
driver = env("SELENIUM_DRIVER", "firefox")
workspace = env("SLACK_WORKSPACE")
email = env("SLACK_EMAIL")
password = env("SLACK_PASSWORD")


# e for element
class E:
    continue_btn = "xpath:/html/body/main/div/div/div/div/div[2]/form/button"
    google_next = "xpath:/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button/div[2]"
    google_password = "xpath://input[@type='password']"
    continue_in_browser = "xpath:/html/body/div[6]/div/div/div/div/div/button"
    slack_new_msg = "xpath:/html/body/div[2]/div/div[2]/div[1]/div/div[1]/button"
    slack_slackbot = (
        "xpath:/html/body/div[6]/div/div/div/div/div/div/div/div/span/div/div/div/div"
    )
    slack_chat_textbox = "xpath:/html/body/div[2]/div/div[2]/div[3]/div/div[2]/div/div/div[3]/div/div[1]/div[1]/div[1]/div[1]"
    emoji_panel = "xpath:/html/body/div[2]/div/div[2]/div[3]/div/div[2]/div/div/div[3]/div/div[1]/div[1]/div[2]/button[3]"
    add_emoji = "xpath:/html/body/div[6]/div/div/div/div/div/div[4]/button"
    upload_emoji = "xpath:/html/body/div[6]/div/div/div[2]/div/div[1]/div/div/div/div/form/ol[1]/li/div[3]/div[3]/button"
    save_emoji = "xpath:/html/body/div[6]/div/div/div[3]/div/button[2]"
    workspace_textbox = "id:domain"
    google_login = "id:google_login_button"
    google_email = "id:identifierId"
    emoji_name = "id:emojiname"
    signin = "text:Sign in"
    manual_login = "text:sign in manually instead"


# putting the slack class here because relative imports are hard
class Slack:
    def __init__(self):
        self._debug = env("DEBUG", False)
        if self._debug:
            print("=== DEBUGGING MODE ===")

        if driver == "firefox":
            self._browser = webdriver.Firefox()
        elif driver == "chrome":
            self._browser = webdriver.Chrome()
        else:
            print(f"Selenium driver {driver} is not supported")
            exit(1)

        self._browser.get(f"https://{workspace}.slack.com/")

    def open_google_login(self):
        # click 'Continue with Google'
        self._click(E.google_login)

    # sign into slack using google account
    def login_with_google(self):
        # email textbox
        self._type(E.google_email, email)
        self._click(E.google_next)

        sleep(2)  # I cant use _waitfor_xpath for some reason here...

        # enter credentials and sign in
        self._type(E.google_password, password)
        self._click(E.google_next)

    def launch_slack_app(self):
        self._waitfor_xpath(E.continue_in_browser).click()
        # bypass the 'launch slack desktop' prompt by going back to the workspace after login
        # self._browser.get(f"https://{workspace}.slack.com")

    def open_chat_with_slackbot(self):
        self._click(E.slack_new_msg)

        actions = ActionChains(self._browser)
        actions.send_keys("Slackbot")
        actions.perform()

        slackbot_entry = self._waitfor_xpath(E.slack_slackbot)
        slackbot_entry.click()
        self._click(E.slack_chat_textbox)

    def open_emoji_panel(self):
        self._click(E.emoji_panel)

    def add_emoji(self, name, filepath):
        self._click(E.add_emoji)
        sleep(0.1)
        self._type(E.emoji_name, name)
        self._click(E.upload_emoji)

        pyautogui.write(filepath)
        pyautogui.press("Enter")

        # dont actually save the emoji if debugging
        if not self._debug:
            self._click(E.save_emoji)

    def _element(self, target):
        if target.startswith("xpath:"):
            xpath = target.split("xpath:")[1]
            return self._browser.find_element_by_xpath(xpath)
        elif target.startswith("id:"):
            html_id = target.split("id:")[1]
            return self._browser.find_element_by_id(html_id)
        elif target.startswith("text:"):
            text = target.split("text:")[1]
            return self._browser.find_element_by_link_text(text)
        else:
            print(f"Invalid target {target}")

    def _click(self, target):
        self._element(target).click()

    def _type(self, target, keys):
        self._element(target).send_keys(keys)

    def close(self):
        self._browser.close()

    def _waitfor_xpath(self, xpath):
        return WebDriverWait(self._browser, 20).until(
            EC.presence_of_element_located((By.XPATH, xpath.split("xpath:")[1]))
        )


def run_proc(command: str) -> str:
    args = command.split(" ")  # turn command into array
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode, result.stdout.decode("utf-8")


# check xclip dependency
if run_proc("which xclip")[0] != 0:
    print("xclip not found!  Please install xclip in order for this to work.")
    print("\tUbuntu/Debian: sudo apt install xclip")
    print("\tArch: pacman -S xclip")

# make sure the clipboard contains an image
if "image/png" in run_proc("xclip -selection clipboard -t TARGETS -o")[1]:
    filepath = f"/tmp/{uuid4()}.png"
    system(f"xclip -selection clipboard -t image/png -o > {filepath}")

    name = argv[1]

    slack = Slack()
    slack.open_google_login()
    slack.login_with_google()
    sleep(0.25)
    slack.launch_slack_app()
    slack.open_chat_with_slackbot()
    slack.open_emoji_panel()
    slack.add_emoji(name, filepath)

    # slack.close()
else:
    print("ERROR: The clipboard does not contain an image.")
    print("Please copy an image first.")
    exit(1)
