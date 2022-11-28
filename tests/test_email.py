import unittest
from random import randrange
from main_logic import *

class MockResponse:
    def __init__(self, status_code, text='{}'):
        self.text = text
        self.status_code = status_code

class TestEmail(unittest.TestCase):
    def test_email(self):
        with open('configs.json', 'r') as f:
            args = json.load(f)
        if 'password' not in args:
            print('no password -> cannot test')
            return 
        args['debug'] = False 
        res = send_email(args, 'Test email', 'Test email')
        self.assertEqual(res, True)