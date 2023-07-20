import unittest
from app.kvstore_app import app


class TestAPI(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_set(self):
        resp = self.app.post('/set', json={'key': 'abc', 'value': '123'})
        self.assertEqual(resp.status_code, 200)

    def test_get(self):
        self.app.post('/set', json={'key': 'xyz', 'value': '456'})
        resp = self.app.get('/get/xyz')
        self.assertEqual(resp.json, {'value': '456'})

    def test_get_not_found(self):
        resp = self.app.get('/get/missing')
        self.assertEqual(resp.status_code, 404)

    def test_search_by_prefix(self):
        self.app.post('/set', json={'key': 'abc-1', 'value': '123'})
        self.app.post('/set', json={'key': 'abc-2', 'value': '456'})
        self.app.post('/set', json={'key': 'xyz-1', 'value': '789'})
        resp = self.app.get('/search?prefix=abc')
        expected = {'abc-1': '123', 'abc-2': '456'}
        self.assertEqual(resp.json, expected)

    def test_search_by_suffix(self):
        self.app.post('/set', json={'key': 'abc-1', 'value': '123'})
        self.app.post('/set', json={'key': 'xyz-1', 'value': '456'})
        self.app.post('/set', json={'key': 'xyz-2', 'value': '789'})
        resp = self.app.get('/search?suffix=-1')
        expected = {'abc-1': '123', 'xyz-1': '456'}
        self.assertEqual(resp.json, expected)


if __name__ == '__main__':
    unittest.main()
