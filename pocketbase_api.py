import requests
import datetime
from aqt import mw

from anki_stats import get_daily_reviews_since, get_time_daily
import consts

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
        
        # token = user["token"]
        user = User(user_data, self)
        
        self.user = user
        
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
        else:
            self.user = None
            
    def save_user_login(self):
        # write user data to config
        config = mw.addonManager.getConfig(consts.ADDON_FOLDER)
        if not config:
            config = {}
        
        config["user_data"] = self.user.model
        mw.addonManager.writeConfig(consts.ADDON_FOLDER, config)
        
    def logout(self):
        self.user = None
        
        # update config data
        config = mw.addonManager.getConfig(consts.ADDON_FOLDER)
        config['user_data'] = None
        
        mw.addonManager.writeConfig(consts.ADDON_FOLDER, config)

class User:
    def __init__(self, user_data, PB):
        self.token = user_data["token"]
        self.id = user_data['record']["id"]
        self.model = user_data['record']
        self.PB = PB
        
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
        success = True
        curr_reviews = self.get_reviews()
        
        date_str = consts.get_date_str(date)
        curr_reviews[date_str] = reviews_number
        
        r = requests.patch(self.PB.url + f"api/collections/user_data/records/{self.model['user_data']}", json={
            "reviews": curr_reviews
        }, headers=self._get_headers())
        success = success and r.status_code == 200
        
        update_lb = self.update_leaderboards(curr_reviews)
        success = success and update_lb
        
        return success

    def set_multiple_reviews(self, reviews):
        curr_reviews = self.get_reviews()
        
        for rev_keys in reviews:
            curr_reviews[rev_keys] = reviews[rev_keys]
        
        r = requests.patch(self.PB.url + f"api/collections/user_data/records/{self.model['user_data']}", json={
            "reviews": curr_reviews
        }, headers=self._get_headers())
        update_lb = self.update_leaderboards(curr_reviews)
        
        return r.status_code == 200 and update_lb

    def update_leaderboards(self, reviews):
        success = True
        
        # get minutes since start of month
        dt = datetime.datetime.now()
        dt = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        minutes = get_time_daily(dt)
        
        update_user_db = False

        # calculate day score
        day_rev_score = 0
        day_min_score = 0
        if consts.get_date_str(datetime.datetime.now()) in reviews:
            day_rev_score = reviews[consts.get_date_str(datetime.datetime.now())]
            day_min_score = minutes[consts.get_date_str(datetime.datetime.now())]
        
        # calculate week score
        week_rev_score = 0
        week_min_score = 0
        start_date = datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())
        while start_date.date() <= datetime.datetime.now().date():
            if consts.get_date_str(start_date) in reviews:
                week_rev_score += reviews[consts.get_date_str(start_date)]
                week_min_score += minutes[consts.get_date_str(start_date)]

            start_date += datetime.timedelta(days=1)
            
        # calculate month score
        month_rev_score = 0
        month_min_score = 0
        start_date = datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().day - 1)
        while start_date.date() <= datetime.datetime.now().date():
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
        
        if update_user_db:
            r = requests.patch(self.PB.url + f"api/collections/users/records/{self.id}", json=self.model, headers=self._get_headers())
            if r.status_code != 200:
                success = False
        
        return success
        
    def full_sync(self):
        reviews = get_daily_reviews_since(datetime.datetime(datetime.datetime.now().year, 1, 1))

        return self.set_multiple_reviews(reviews)
