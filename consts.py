VERSION = "0.4.7"
APP_NAME = "NeoLeaderBoard"
SHORT_APP_NAME = "NeoLB"

VERSION_UNSTABLE = VERSION[0] == "0"

import pathlib, os

POCKETBASE_URL = 'https://pb-anki-lb.fly.dev/'
ADDON_FOLDER = os.path.basename(pathlib.Path(__file__).parent.resolve())

LEADERBOARD_WEBSITE = 'https://neoankilb.vercel.app/'


def get_date_str(date):
    return date.strftime("%Y-%m-%d")

DEV_MODE = ADDON_FOLDER.endswith("dev")
