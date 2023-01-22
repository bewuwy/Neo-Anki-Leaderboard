import pathlib, os

POCKETBASE_URL = 'https://pb-anki-lb.fly.dev/'
ADDON_FOLDER = os.path.basename(pathlib.Path(__file__).parent.resolve())

LEADERBOARD_WEBSITE = 'https://neo-anki-leaderboard.vercel.app/'


def get_date_str(date):
    return date.strftime("%Y-%m-%d")

DEV_MODE = False
