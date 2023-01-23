import requests
import datetime
from aqt import mw

from anki_stats import get_daily_reviews_since
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
        r0 = requests.get(self.PB.url + f"api/collections/users/records/{self.id}/", headers=self._get_headers())
        
        if r0.status_code != 200:
            return False
        
        # user_data_id = r0.json()["user_data"]
        user_today = r0.json()["user_today"]
        user_week = r0.json()["user_week"]
        user_month = r0.json()["user_month"]

        # calculate day score
        day_score = 0        
        if consts.get_date_str(datetime.datetime.now()) in reviews:
            day_score = reviews[consts.get_date_str(datetime.datetime.now())]
        
        r_day = requests.patch(self.PB.url + f"api/collections/today_leaderboard/records/{user_today}", json={
            "reviews": day_score
        }, headers=self._get_headers())
        
        # calculate week score
        week_score = 0
        start_date = datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())
        while start_date.date() <= datetime.datetime.now().date():
            if consts.get_date_str(start_date) in reviews:
                week_score += reviews[consts.get_date_str(start_date)]
            start_date += datetime.timedelta(days=1)
        
        r_week = requests.patch(self.PB.url + f"api/collections/week_leaderboard/records/{user_week}", json={
            "reviews": week_score
        }, headers=self._get_headers())
        
        # calculate month score
        month_score = 0
        start_date = datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().day - 1)
        while start_date.date() <= datetime.datetime.now().date():
            if consts.get_date_str(start_date) in reviews:
                month_score += reviews[consts.get_date_str(start_date)]
            start_date += datetime.timedelta(days=1)
        
        r_month = requests.patch(self.PB.url + f"api/collections/month_leaderboard/records/{user_month}", json={
            "reviews": month_score
        }, headers=self._get_headers())
            
        return r_day.status_code == 200 and r_week.status_code == 200 and r_month.status_code == 200 
        # {
        #     "day": day_score,
        #     "week": week_score,
        #     "month": month_score
        # }
        
    def full_sync(self):
        reviews = get_daily_reviews_since(datetime.datetime(datetime.datetime.now().year, 1, 1))

        return self.set_multiple_reviews(reviews)
