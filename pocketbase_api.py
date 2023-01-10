import requests

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
        user = User(user_data, self)
        self.user = user

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
        r = requests.get(self.PB.url + f"api/collections/users/records/{self.id}/", headers=self._get_headers())
            
        data = r.json()        
        curr_reviews = data["reviews"]
        
        if not curr_reviews:
            curr_reviews = {}
            
        date_str = date.strftime("%Y-%m-%d")
        
        curr_reviews[date_str] = reviews_number
        
        r = requests.patch(self.PB.url + f"api/collections/users/records/{self.id}", json={
            "reviews": curr_reviews
        }, headers=self._get_headers())
        
        return r.status_code == 200
