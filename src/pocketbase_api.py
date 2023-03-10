import requests
import datetime
from aqt import mw

import anki_stats
from anki_stats import get_daily_reviews_since
import consts

from dev import *

class UpdateLBError(Exception):
    pass

class PB:
    def __init__(self, url):
        self.url = url
        self.user = None
        self.last_sync: datetime.datetime = datetime.datetime.fromtimestamp(
            mw.addonManager.getConfig(consts.ADDON_FOLDER).get("last_sync", TIMESTAMP_0))

    def login(self, username, password):
        r = requests.post(self.url + "api/collections/users/auth-with-password", json={
                "identity": username,
                "password": password
            })
        
        user_data = r.json()
        
        if user_data is None or "token" not in user_data:
            return None
        
        user = User(user_data, self)
        self.user = user
        
        log(f"Logged in user {self.user.id}")
        
    def login_from_data(self, user_data):
        if user_data: 

            # TODO: deprecate in 1.0
            if "user_data" not in user_data['record']:
                # get user record from pocketbase
                r = requests.get(self.url + f"api/collections/users/records/{user_data['record']['id']}", headers={
                    "Authorization": f"{user_data['token']}"
                })
                
                user_data['record'] = r.json()
                
                user = User(user_data, self)
                self.user = user
                
                self.save_user_login()

            else:            
                user = User(user_data, self)
                self.user = user
                
            log(f"Logged in user {self.user.id} from data")
        else:
            self.user = None
            
            log("No user data found")
            
    def refresh_user_token(self):
        """Refreshes pocketbase user token

        Returns:
            bool: success
        """
        
        r = requests.post(self.url + f"api/collections/users/auth-refresh", headers=self.user._get_headers())
        
        if r.status_code != 200:
            log("Failed to refresh user token")
            log(r.json())
            return False
        
        self.user = User(r.json(), self)
        self.save_user_login()
        
        log(f"Refreshed user token {self.user.id}")
        return True
        
    def save_user_login(self):
        """write user data to config
        """
        
        config = mw.addonManager.getConfig(consts.ADDON_FOLDER)
        if not config:
            config = {}
        
        config["last_sync"] = self.last_sync.timestamp()
        config["user_data"] = {
            "record": self.user.model,
            "token": self.user.token,
        }
        mw.addonManager.writeConfig(consts.ADDON_FOLDER, config)
        
        log(f"Saved user data {self.user.id} to config")
        
    def logout(self):
        self.user = None
        
        # update config data
        config = mw.addonManager.getConfig(consts.ADDON_FOLDER)
        config['user_data'] = None
        config['medals'] = []
        
        mw.addonManager.writeConfig(consts.ADDON_FOLDER, config)
        
        log("Logged out user")
        
        self = None

class User:
    def __init__(self, user_data, PB: PB):
        self.token = user_data["token"]
        self.id = user_data['record']["id"]
        self.model = user_data['record']
        self.PB = PB
        
        # TODO: deprecate in 1.0 after pb rework
        #! check if user has user_data record
        if self.model['user_data'] == "":
            log("User has no user_data record")
            
            r = requests.post(self.PB.url + "api/collections/user_data/records", json={
                "user": self.id
            }, headers=self._get_headers())
            
            if r.status_code != 200:
                log("Failed to create user_data record")
                log(r.json())
                self = None
                return
            
            user_data_id = r.json()['id']
            self.model['user_data'] = user_data_id
            
            r = requests.patch(self.PB.url + f"api/collections/users/records/{self.id}", json=self.model, headers=self._get_headers())
            
            if r.status_code != 200:
                log("Failed to update user record with user_data id")
                log(r.json())
                self = None
                return
            
            log("Created user_data record")
        
    def _get_headers(self):
        return {
            "Authorization": f"{self.token}"
        }
    
    def change_name(self, new_name):
        r = requests.patch(self.PB.url + f"api/collections/users/records/{self.id}", json={
            "name": new_name
        }, headers=self._get_headers())
        
        return r.status_code == 200
    
    def get_user_data(self):
        """Get user data from pocketbase

        Returns:
            dict: user data
        """
        
        user_data_id = self.model["user_data"]
        
        r = requests.get(self.PB.url + f"api/collections/user_data/records/{user_data_id}/", headers=self._get_headers())
        data = r.json()
        
        return data

    def get_medals(self):
        user_id = self.model["id"]
        
        r_filter = f"owner=\"{user_id}\""
        r = requests.get(self.PB.url + f"api/collections/medals/records/?filter={r_filter}", 
                         headers=self._get_headers())

        if r.status_code != 200:
            log('get medals failed')
            log(r.json())
            return []
        
        return r.json()['items']

    def update_pb_data(self, reviews: dict, curr_streak:int=-1, highest_streak:int=-1):
        """Set multiple reviews at once in pocketbase, then update user's leaderboards

        Args:
            reviews (dict): reviews to set
            curr_streak (int): current streak
            highest_streak (int): highest streak

        Returns:
            bool: success
        """
        
        curr_data = self.get_user_data()
        
        for rev_keys in reviews:
            curr_data["reviews"][rev_keys] = reviews[rev_keys]
        
        if curr_streak >= 0:
            curr_data["streak_current"] = curr_streak
        if highest_streak >= 0:
            curr_data["streak_highest"] = max(curr_data["streak_highest"], highest_streak)
        
        r = requests.patch(self.PB.url + f"api/collections/user_data/records/{self.model['user_data']}", 
                           json=curr_data, headers=self._get_headers())
        
        update_lb = self.update_leaderboards()
        
        if r.status_code != 200:
            log('set multiple reviews failed')
            log(r.json())
        
        return r.status_code == 200 and update_lb

    def update_leaderboards(self):
        """Update user's leaderboards on pocketbase

        Raises:
            UpdateLBError: if update failed

        Returns:
            bool: success
        """
        
        success = True
        
        # get stats since start of month minus a week, because sometimes week is earlier than month
        dt_start = datetime.datetime.utcnow()
        dt_start = dt_start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        dt_start -= datetime.timedelta(days=7)
        
        stats = anki_stats.get_stats_daily_since(dt_start)
        
        update_user_db = False

        # calculate day score
        day_score = {}
        if consts.get_date_str(datetime.datetime.utcnow()) in stats:
            day_score = stats[consts.get_date_str(datetime.datetime.utcnow())]
        
        # calculate week score
        start_date = datetime.datetime.utcnow() - datetime.timedelta(days=datetime.datetime.utcnow().weekday())
        log(f"counting week score from {start_date}")
        week_score = {
            "reviews": 0,
            "minutes": 0,
            "xp": 0,
        }
        while start_date.date() <= datetime.datetime.utcnow().date():
            if consts.get_date_str(start_date) in stats:
                week_score["reviews"] += stats[consts.get_date_str(start_date)]["reviews"]
                week_score["minutes"] += stats[consts.get_date_str(start_date)]["minutes"]
                week_score["xp"] += stats[consts.get_date_str(start_date)]["xp"]

            start_date += datetime.timedelta(days=1)
            
        # calculate month score
        start_date = datetime.datetime.utcnow() - datetime.timedelta(days=datetime.datetime.utcnow().day - 1)
        log(f"counting month score from {start_date}")
        month_score = {
            "reviews": 0,
            "minutes": 0,
            "xp": 0,
        }
        while start_date.date() <= datetime.datetime.utcnow().date():
            if consts.get_date_str(start_date) in stats:
                month_score["reviews"] += stats[consts.get_date_str(start_date)]["reviews"]
                month_score["minutes"] += stats[consts.get_date_str(start_date)]["minutes"]
                month_score["xp"] += stats[consts.get_date_str(start_date)]["xp"]

            start_date += datetime.timedelta(days=1)
        
        # update pb collections
        for collection, score in [("today", day_score), ("week", week_score), ("month", month_score)]:
            if not score:
                log(f"no {collection} score")
                continue
            
            log(score)
            
            db_id = self.model.get(f'user_{collection}')
            reviews, minutes, xp = score["reviews"], score["minutes"], score["xp"]
            json_data = {
                "reviews": reviews,
                "time": minutes,
                "xp": xp
            }
            
            if db_id:                
                r = requests.patch(self.PB.url + f"api/collections/{collection}_leaderboard/records/{db_id}", 
                                   json=json_data, headers=self._get_headers())
            else:
                r = requests.post(self.PB.url + f"api/collections/{collection}_leaderboard/records/", 
                                  json=json_data, headers=self._get_headers())
                
                self.model[f'user_{collection}'] = r.json()['id']
                update_user_db = True
                
            if r.status_code != 200:
                success = False
                
                log(f'update {collection} leaderboard failed')
                log(r.url)
                log(r.json())
                
                raise UpdateLBError(f'update {collection} leaderboard failed')
            
            log(f'updated {collection} leaderboard with {score}')
        
        if update_user_db:
            r = requests.patch(self.PB.url + f"api/collections/users/records/{self.id}", json=self.model, headers=self._get_headers())
            log(f'updated user db')
            
            if r.status_code != 200:
                success = False
                log('update user db failed')
                log(r.json())
        
        return success
    
    def sync(self):
        """Sync reviews, streak and lb since last sync to pocketbase
        """
        
        last_sync = self.PB.last_sync
        
        reviews, _ = get_daily_reviews_since(last_sync)
        self.update_pb_data(reviews)
        
        self.PB.last_sync = datetime.datetime.utcnow()
        self.PB.save_user_login()
    
    def full_sync(self):
        """Sync all reviews since the beginning of the year to pocketbase (for heatmap purposes)

        Returns:
            bool: success
        """
        
        reviews, streak = get_daily_reviews_since(datetime.datetime.fromtimestamp(TIMESTAMP_0))
        
        log(f'Full sync start')
        log(f'{len(reviews)} days with reviews found')
        log(f'{streak} days streak')

        return self.update_pb_data(reviews, curr_streak=streak["current"], highest_streak=streak["highest"])
