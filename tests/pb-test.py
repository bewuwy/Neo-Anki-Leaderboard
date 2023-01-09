import unittest

class TestPocketBase(unittest.TestCase):
    def test_lib(self):
        from pocketbase import PocketBase

        pb = PocketBase("https://pb-anki-lb.fly.dev/")

        test_user = pb.users.auth_via_email("test@bewu.dev", "bewu1234")
        # assert test_user is not None
        self.assertIsNotNone(test_user)

        # print(test_user)


    def test_requests(self):
        import requests
        
        r = requests.post("https://pb-anki-lb.fly.dev/api/collections/users/auth-with-password", json={
            "identity": "test@bewu.dev",
            "password": "bewu1234"
        })
        
        test_user = r.json()
        # assert test_user is not None
        self.assertIsNotNone(test_user)
        
        print(test_user)

if __name__ == "__main__":
    unittest.main()
