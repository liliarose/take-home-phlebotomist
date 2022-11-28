import unittest
from random import randrange
from main_logic import *

class MockResponse:
    def __init__(self, status_code, text='{}'):
        self.text = text
        self.status_code = status_code

class TestGetFeatures(unittest.TestCase):
    def test_bad_status_code(self):
        status_code = randrange(300, 600)
        r = MockResponse(status_code)
        self.assertEqual(get_features(r), None)

    def test_no_response_text(self):
        status_code = randrange(100, 201)
        r = MockResponse(status_code)
        self.assertEqual(get_features(r), None)

    def test_empty_response_text(self):
        status_code = randrange(100, 201)
        text = ''
        r = MockResponse(status_code, text)
        self.assertEqual(get_features(r), None)
    
    def test_missing_auth(self):
        status_code = randrange(100, 201)
        text = '{"message":"Missing Authentication Token"}'
        r = MockResponse(status_code, text)
        self.assertEqual(get_features(r), None)

    def test_no_features(self):
        status_code = randrange(100, 201)
        text = '{"type":"FeatureCollection","features":[]}'
        r = MockResponse(status_code, text)
        self.assertEqual(get_features(r), [])
    
    def test_empty_features(self):
        status_code = randrange(100, 201)
        text = '{"type":"FeatureCollection","features":[{},{}]}'
        r = MockResponse(status_code, text)
        self.assertEqual(get_features(r), [{},{}])
    
    # def test_missing_polygon(self):
    #     status_code = randrange(100, 201)
    #     text = '{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":[-121.93296432495117,37.29139890536388]}}]}'
    #     r = MockResponse(status_code, text)
    #     self.assertEqual(get_features(r), None)
    
    # def test_missing_point(self):
    #     status_code = randrange(100, 201)
    #     text = '{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-121.93416595458983,37.305464062126],[-121.96420669555664,37.27036454209622],[-121.91150665283203,37.27186719156333],[-121.93416595458983,37.305464062126]]]}}]}'
    #     r = MockResponse(status_code, text)
    #     self.assertEqual(get_features(r), None)

    def test_good_status_code(self):
        status_code = randrange(100, 201)
        text = '{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":[-121.93296432495117,37.29139890536388]}},{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-121.93416595458983,37.305464062126],[-121.96420669555664,37.27036454209622],[-121.91150665283203,37.27186719156333],[-121.93416595458983,37.305464062126]]]}}]}'
        json_txt = json.loads(text)
        r = MockResponse(status_code, text)
        self.assertEqual(get_features(r), json_txt['features'])
