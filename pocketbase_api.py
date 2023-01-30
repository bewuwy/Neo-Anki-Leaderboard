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
            user = User(user_data, self)
            self.user = user
        else:
            self.user = None
        
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
    
    def get_reviews(self, date):
        r = requests.get(self.PB.url + f"api/collections/users/records/{self.id}/", headers=self._get_headers())
            
        data = r.json()        
        reviews = data["reviews"]
        
        date_str = date.strftime("%Y-%m-%d")
        
        if not reviews or date_str not in reviews:
            return None
        else:
            return reviews[date_str]
            
    def set_reviews(self, date, reviews_number):   
        r0 = requests.get(self.PB.url + f"api/collections/users/records/{self.id}/", headers=self._get_headers())
        
        if r0.status_code != 200:
            return False
        
        user_data_id = r0.json()["user_data"]
        
        r = requests.get(self.PB.url + f"api/collections/user_data/records/{user_data_id}/", headers=self._get_headers())
        data = r.json()
        
        curr_reviews = data["reviews"]
        if not curr_reviews:
            curr_reviews = {}
        
        date_str = consts.get_date_str(date)
        curr_reviews[date_str] = reviews_number
                
        r = requests.patch(self.PB.url + f"api/collections/user_data/records/{user_data_id}", json={
            "reviews": curr_reviews
        }, headers=self._get_headers())
        
        update_lb = self.update_leaderboards(curr_reviews)
        
        return r.status_code == 200 and update_lb

    def set_multiple_reviews(self, reviews):
        r0 = requests.get(self.PB.url + f"api/collections/users/records/{self.id}/", headers=self._get_headers())
        
        if r0.status_code != 200:
            return False
        
        user_data_id = r0.json()["user_data"]
        # user_today_id = r0.json()["user_today"]
        
        r = requests.get(self.PB.url + f"api/collections/user_data/records/{user_data_id}/", headers=self._get_headers())
        data = r.json()
        
        curr_reviews = data["reviews"]
        if not curr_reviews:
            curr_reviews = {}
        
        for rev_keys in reviews:
            curr_reviews[rev_keys] = reviews[rev_keys]
        
        r = requests.patch(self.PB.url + f"api/collections/user_data/records/{user_data_id}", json={
            "reviews": curr_reviews
        }, headers=self._get_headers())
        
        update_lb = self.update_leaderboards(curr_reviews)
        
        return r.status_code == 200 and update_lb

    def update_leaderboards(self, reviews):
        sucess = True
        
        r0 = requests.get(self.PB.url + f"api/collections/users/records/{self.id}/", headers=self._get_headers())
        
        if r0.status_code != 200:
            return False
        
        # get minutes since start of month
        dt = datetime.datetime.now()
        dt = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        minutes = get_time_daily(dt)
        
        user_db = r0.json()
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
            
            db_id = user_db.get(f'user_{collection}')
            
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
                
                user_db[f'user_{collection}'] = r.json()['id']
                update_user_db = True
                
            if r.status_code != 200:
                sucess = False
        
        if update_user_db:
            r = requests.patch(self.PB.url + f"api/collections/users/records/{self.id}", json=user_db, headers=self._get_headers())
            if r.status_code != 200:
                sucess = False
        
        return sucess
        
    def full_sync(self):
        reviews = get_daily_reviews_since(datetime.datetime(datetime.datetime.now().year, 1, 1))

        return self.set_multiple_reviews(reviews)
