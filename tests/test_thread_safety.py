import threading
import unittest
from openapi_python_sdk import Client, OauthClient
import httpx

class TestThreadSafety(unittest.TestCase):
    def test_oauth_client_thread_safety(self):
        oauth = OauthClient(username="user", apikey="key")

        clients = []
        def get_client():
            clients.append(oauth.client)

        threads = [threading.Thread(target=get_client) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Each thread should have gotten a unique client instance
        self.assertEqual(len(clients), 5)
        self.assertEqual(len(set(id(c) for c in clients)), 5)

    def test_client_thread_safety(self):
        client = Client(token="tok")

        clients = []
        def get_client():
            clients.append(client.client)

        threads = [threading.Thread(target=get_client) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Each thread should have gotten a unique client instance
        self.assertEqual(len(clients), 5)
        self.assertEqual(len(set(id(c) for c in clients)), 5)

    def test_shared_client_injection_still_works(self):
        # If we explicitly pass a client, it SHOULD be shared (backward compatibility)
        shared_engine = httpx.Client()
        oauth = OauthClient(username="user", apikey="key", client=shared_engine)

        clients = []
        def get_client():
            clients.append(oauth.client)

        threads = [threading.Thread(target=get_client) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All threads should have the SAME instance because it was injected
        self.assertEqual(len(clients), 5)
        self.assertEqual(len(set(id(c) for c in clients)), 1)
        self.assertEqual(id(clients[0]), id(shared_engine))

if __name__ == "__main__":
    unittest.main()
