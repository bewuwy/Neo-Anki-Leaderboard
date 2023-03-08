import requests
import datetime
from aqt import mw

from anki_stats import get_daily_reviews_since, get_time_daily
import consts

from dev import *

class UpdateLBError(Exception):
    pass

class PB:
    def __init__(self, url):
        self.url = url
        self.user = None

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
        # write user data to config
        config = mw.addonManager.getConfig(consts.ADDON_FOLDER)
        if not config:
            config = {}
        
        config["user_data"] = {
            "record": self.user.model,
            "token": self.user.token
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
    def __init__(self, user_data, PB):
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
    
    def get_reviews(self):
        user_data_id = self.model["user_data"]
        
        r = requests.get(self.PB.url + f"api/collections/user_data/records/{user_data_id}/", headers=self._get_headers())
        data = r.json()
        
        curr_reviews = data["reviews"]
        if not curr_reviews:
            curr_reviews = {}
        
        return curr_reviews
    
    def set_reviews(self, date, reviews_number):
        curr_reviews = self.get_reviews()
        
        date_str = consts.get_date_str(date)
        curr_reviews[date_str] = reviews_number
        
        r = requests.patch(self.PB.url + f"api/collections/user_data/records/{self.model['user_data']}", json={
            "reviews": curr_reviews
        }, headers=self._get_headers())        
        update_lb = self.update_leaderboards(curr_reviews)
        
        if r.status_code != 200:
            log('set reviews failed')
            log(r.json())
        
        return r.status_code == 200 and update_lb

    def set_multiple_reviews(self, reviews):
        curr_reviews = self.get_reviews()
        
        for rev_keys in reviews:
            curr_reviews[rev_keys] = reviews[rev_keys]
        
        r = requests.patch(self.PB.url + f"api/collections/user_data/records/{self.model['user_data']}", json={
            "reviews": curr_reviews
        }, headers=self._get_headers())
        update_lb = self.update_leaderboards(curr_reviews)
        
        if r.status_code != 200:
            log('set multiple reviews failed')
            log(r.json())
        
        return r.status_code == 200 and update_lb

    def get_medals(self):
        user_id = self.model["id"]
        
        r_filter = f"owner=\"{user_id}\""
        r = requests.get(self.PB.url + f"api/collections/medals/records/?filter={r_filter}", headers=self._get_headers())

        if r.status_code != 200:
            log('get medals failed')
            log(r.json())
            return []
        
        return r.json()['items']

    def update_leaderboards(self, reviews):
        success = True
        
        # get minutes since start of month minus a week, because sometimes week is earlier than month
        dt = datetime.datetime.utcnow()
        dt = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        dt -= datetime.timedelta(days=7)
        
        minutes = get_time_daily(dt)
        
        update_user_db = False

        # calculate day score
        day_rev_score = 0
        day_min_score = 0
        if consts.get_date_str(datetime.datetime.utcnow()) in reviews:
            day_rev_score = reviews[consts.get_date_str(datetime.datetime.utcnow())]
            day_min_score = minutes[consts.get_date_str(datetime.datetime.utcnow())]
        
        # calculate week score
        week_rev_score = 0
        week_min_score = 0
        start_date = datetime.datetime.utcnow() - datetime.timedelta(days=datetime.datetime.utcnow().weekday())
        log(f"counting week score from {start_date}")
        while start_date.date() <= datetime.datetime.utcnow().date():
            if consts.get_date_str(start_date) in reviews:
                week_rev_score += reviews[consts.get_date_str(start_date)]
                week_min_score += minutes[consts.get_date_str(start_date)]

            start_date += datetime.timedelta(days=1)
            
        # calculate month score
        month_rev_score = 0
        month_min_score = 0
        start_date = datetime.datetime.utcnow() - datetime.timedelta(days=datetime.datetime.utcnow().day - 1)
        log(f"counting month score from {start_date}")
        while start_date.date() <= datetime.datetime.utcnow().date():
            if consts.get_date_str(start_date) in reviews:
                month_rev_score += reviews[consts.get_date_str(start_date)]
                month_min_score += minutes[consts.get_date_str(start_date)]
            
            start_date += datetime.timedelta(days=1)
        
        for collection, score, time in \
            zip(["today", "week", "month"], 
                [day_rev_score, week_rev_score, month_rev_score], 
                [day_min_score, week_min_score, month_min_score]):
            
            db_id = self.model.get(f'user_{collection}')
            
            if db_id:                
                r = requests.patch(self.PB.url + f"api/collections/{collection}_leaderboard/records/{db_id}", json={
                    "reviews": score,
                    "time": time
                }, headers=self._get_headers())
            else:
                r = requests.post(self.PB.url + f"api/collections/{collection}_leaderboard/records/", json={
                    "user": self.id,
                    "reviews": score,
                    "time": time
                }, headers=self._get_headers())
                
                self.model[f'user_{collection}'] = r.json()['id']
                update_user_db = True
                
            if r.status_code != 200:
                success = False
                
                log(f'update {collection} leaderboard failed')
                log(r.url)
                log(r.json())
                
                raise UpdateLBError(f'update {collection} leaderboard failed')
            
            log(f'updated {collection} leaderboard with {score} reviews and {time} minutes')
        
        if update_user_db:
            r = requests.patch(self.PB.url + f"api/collections/users/records/{self.id}", json=self.model, headers=self._get_headers())
            log(f'updated user db')
            
            if r.status_code != 200:
                success = False
                log('update user db failed')
                log(r.json())
        
        return success
        
    def full_sync(self):
        reviews = get_daily_reviews_since(datetime.datetime(datetime.datetime.utcnow().year, 1, 1))
        
        log(f'full sync')

        return self.set_multiple_reviews(reviews)
