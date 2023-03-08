VERSION = "0.6"
APP_NAME = "NeoLeaderBoard"
SHORT_APP_NAME = "NeoLB"

VERSION_UNSTABLE = VERSION[0] == "0"

import pathlib, os

POCKETBASE_URL = 'https://pb-anki-lb.fly.dev/'
ADDON_FOLDER = os.path.basename(pathlib.Path(__file__).parent.resolve())

LEADERBOARD_WEBSITE = 'https://neoankilb.vercel.app/'
GITHUB_URL = "https://github.com/bewuwy/Neo-Anki-Leaderboard/"

import datetime
def get_date_str(date=None):
    if date is None:
        date = datetime.datetime.utcnow()
    
    return date.strftime("%Y-%m-%d")

DEV_MODE = ADDON_FOLDER.endswith("dev")
