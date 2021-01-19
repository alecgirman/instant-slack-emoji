# instant-slack-emoji
Quickly create a slack emoji

### installation

```sh
sudo apt install python3-dev python3-tk
pip3 install webdrivermanager selenium pyautogui python-dotenv envs
sudo webdrivermanager firefox chrome
```

#### Configuring your env file

Insert the following fields into your .env:

SLACK_EMAIL: the email to login with slack.

SLACK_PASSWORD: your slack password

SLACK_WORKSPACE: the name of your slack workspace ([workspace].slack.com)

### usage

First, take a screenshot and use your screenshot utility to copy the image (not the filename, but the image data itself) into your clipboard

Then, run the following command.
```sh
python3 ise.py <name of emoji>```
