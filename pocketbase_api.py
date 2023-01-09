import requests


class PB:
    def __init__(self, url):
        self.url = url

    def login(self, user, password):
        r = requests.post(self.url + "api/collections/users/auth-with-password", json={
                "identity": user,
                "password": password
            })
            
        user = r.json()
        
        if user is None or "token" not in user:
            return None
        
        token = user["token"]
        
        return token
