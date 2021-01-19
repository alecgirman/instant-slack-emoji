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

# TODO: click() and text() function in Slack api
# TODO: go straight to workspace login
# TODO: get to browser slack faster


# putting the slack class here because relative imports are hard
class Slack:
    def __init__(self):
        if driver == "firefox":
            self._browser = webdriver.Firefox()
        elif driver == "chrome":
            self._browser = webdriver.Chrome()
        else:
            print(f"Selenium driver {driver} is not supported")
            exit(1)

        self._debug = env("DEBUG")
        self._browser.get("https://slack.com/")

    def open_google_login(self):
        # click sign in button
        login_button = self._browser.find_element_by_link_text("Sign in")
        login_button.click()

        # click button to sign in manually (do not send a code to email)
        manual_login = self._browser.find_element_by_link_text(
            "sign in manually instead"
        )

        manual_login.click()

        # Type the workspace name into the textbox with '.slack.com'
        workspace_xpath = '//*[@id="domain"]'
        workspace_textbox = self._browser.find_element_by_xpath(workspace_xpath)
        workspace_textbox.send_keys(workspace)

        # click 'Continue'
        continue_xpath = "/html/body/main/div/div/div/div/div[2]/form/button"
        self._browser.find_element_by_xpath(continue_xpath).click()

        # click 'Continue with Google'
        google_xpath = '//*[@id="google_login_button"]'
        self._browser.find_element_by_xpath(google_xpath).click()

    # sign into slack using google account
    def login_with_google(self):
        # next button
        next_xpath = "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button/div[2]"

        # email textbox
        email_xpath = '//*[@id="identifierId"]'
        self._browser.find_element_by_xpath(email_xpath).send_keys(email)
        self._browser.find_element_by_xpath(next_xpath).click()

        sleep(2)  # I cant use _waitfor_xpath for some reason here...
        password_xpath = "//input[@type='password']"

        # enter credentials and sign in
        self._browser.find_element_by_xpath(password_xpath).send_keys(password)
        self._browser.find_element_by_xpath(next_xpath).click()

    def continue_in_browser(self):
        self._waitfor_xpath("/html/body/div[6]/div/div/div/div/div/button").click()

    def open_chat_with_slackbot(self):
        new_msg_xpath = "/html/body/div[2]/div/div[2]/div[1]/div/div[1]/button"
        self._browser.find_element_by_xpath(new_msg_xpath).click()

        actions = ActionChains(self._browser)
        actions.send_keys("Slackbot")
        actions.perform()

        slackbot_entry = self._waitfor_xpath(
            "/html/body/div[6]/div/div/div/div/div/div/div/div/span/div/div/div/div"
        )
        slackbot_entry.click()
        chat_xpath = "/html/body/div[2]/div/div[2]/div[3]/div/div[2]/div/div/div[3]/div/div[1]/div[1]/div[1]/div[1]"
        self._browser.find_element_by_xpath(chat_xpath).click()

    def open_emoji_panel(self):
        emoji_xpath = "/html/body/div[2]/div/div[2]/div[3]/div/div[2]/div/div/div[3]/div/div[1]/div[1]/div[2]/button[3]"
        self._browser.find_element_by_xpath(emoji_xpath).click()

    def add_emoji(self, name, filepath):
        add_emoji_xpath = "/html/body/div[6]/div/div/div/div/div/div[4]/button"
        self._browser.find_element_by_xpath(add_emoji_xpath).click()
        sleep(0.1)
        self._browser.find_element_by_id("emojiname").send_keys(name)
        upload_xpath = "/html/body/div[6]/div/div/div[2]/div/div[1]/div/div/div/div/form/ol[1]/li/div[3]/div[3]/button"
        self._browser.find_element_by_xpath(upload_xpath).click()

        pyautogui.write(filepath)
        pyautogui.press("Enter")

        save_xpath = "/html/body/div[6]/div/div/div[3]/div/button[2]"

        # dont actually save the emoji if debugging
        if not self._debug:
            self._browser.find_element_by_xpath(save_xpath).click()

    def close(self):
        self._browser.close()

    def _waitfor_xpath(self, xpath):
        return WebDriverWait(self._browser, 20).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )


def run_proc(command: str) -> str:
    args = command.split(" ")  # turn command into array
    result = subprocess.run(args, stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8")


# check xclip dependency
if "not found" in run_proc("which xlip"):
    print("xclip not found!  Please install xclip in order for this to work.")
    print("\tUbuntu/Debian: sudo apt install xclip")
    print("\tArch: pacman -S xclip")


# make sure the clipboard contains an image
if "image/png" in run_proc("xclip -selection clipboard -t TARGETS -o"):
    filepath = f"/tmp/{uuid4()}.png"
    system(f"xclip -selection clipboard -t image/png -o > {filepath}")

    name = argv[1]

    slack = Slack()
    slack.open_google_login()
    slack.login_with_google()
    slack.continue_in_browser()
    slack.open_chat_with_slackbot()
    slack.open_emoji_panel()
    slack.add_emoji(name, filepath)

    # slack.close()
else:
    print("ERROR: The clipboard does not contain an image.")
    print("Please copy an image first.")
    exit(1)
