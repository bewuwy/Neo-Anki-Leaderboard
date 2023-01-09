import unittest
import os

import sys
# check if system is windows
if sys.platform.startswith("win"):
    sys.path.append( os.path.join(os.getenv('APPDATA'), 'Anki2', 'addons21', 'neo-leaderboard'))
    
from pocketbase_api import PB
from consts import POCKETBASE_URL

import random
import datetime

class TestPocketBase(unittest.TestCase):
    
    @unittest.skip("PB Library not working")
    def test_lib(self):
        from pocketbase import PocketBase

        pb = PocketBase(POCKETBASE_URL)

        test_user = pb.users.auth_via_email("test@bewu.dev", "bewu1234")
        # assert test_user is not None
        self.assertIsNotNone(test_user)

        # print(test_user)


    def test_requests(self):
        import requests
        
        r = requests.post(POCKETBASE_URL + "api/collections/users/auth-with-password", json={
            "identity": "test@bewu.dev",
            "password": "bewu1234"
        })
        
        test_user = r.json()
        # assert test_user is not None
        self.assertIsNotNone(test_user)
        
        # print(test_user)
        
    def test_change_name(self):
        pb = PB(POCKETBASE_URL)
        
        pb.login("test@bewu.dev", "bewu1234")
        
        s = pb.user.change_name(f"test { random.randint(0, 1000) }")
        
        self.assertTrue(s)
        
    def test_get_reviews(self):
        pb = PB(POCKETBASE_URL)
        
        pb.login("test@bewu.dev", "bewu1234")
        
        r = pb.user.get_reviews(datetime.datetime.now())
        
        
        
    def test_update_reviews(self):
        pb = PB(POCKETBASE_URL)
        
        pb.login("test@bewu.dev", "bewu1234")
        
        r = pb.user.set_reviews(datetime.datetime.now(), 69)
        
        self.assertTrue(r)

if __name__ == "__main__":
    unittest.main()
