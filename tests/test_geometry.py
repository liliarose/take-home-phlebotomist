import unittest
from main_logic import *

depends = [
    {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [-122.03287124633789, 37.35232882898717]}}, {"type": "Feature", "properties": {}, "geometry": {
        "type": "Polygon", "coordinates": [[[-122.04145431518556, 37.344368504994286], [-122.0328712463379, 37.344368504994286], [-122.0328712463379, 37.35760507144896], [-122.04145431518556, 37.35760507144896], [-122.04145431518556, 37.344368504994286]]]}}]}
]
in_bounds = [
    {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [-121.93296432495117, 37.29139890536388]}}, {"type": "Feature", "properties": {}, "geometry": {
        "type": "Polygon", "coordinates": [[[-121.93416595458983, 37.305464062126], [-121.96420669555664, 37.27036454209622], [-121.91150665283203, 37.27186719156333], [-121.93416595458983, 37.305464062126]]]}}]},
        # weird case w/ 2 polygons but only 1 polygon feature
    {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [-122.28693008422852, 37.51483205774519]}}, {"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-122.30946063995361, 37.548218088360116],                                                                                                                                                                                                                                                                     [-122.31645584106445, 37.53875852887022], [-122.29770183563231, 37.53882658754147], [-122.30946063995361, 37.548218088360116]], [[-122.28710174560547, 37.52000599905024], [-122.29216575622559, 37.51251728365287], [-122.28238105773926, 37.513130024958315], [-122.28710174560547, 37.52000599905024]]]}}]},
]
out_of_bounds = [
    {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [-121.94340047836305, 37.31784231997199]}}, {"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-121.93468093872069, 37.33631625612842], [-121.96249008178712,
                                                                                                                                                                                                                                                                                                                37.33617976989369], [-121.96523666381836, 37.304644804751106], [-121.93708419799805, 37.30491789153446], [-121.93777084350586, 37.31761533167621], [-121.95150375366211, 37.316796206705085], [-121.95219039916992, 37.32607910032697], [-121.93708419799805, 37.32648861334206], [-121.93468093872069, 37.33631625612842]]]}}]},
    {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [-122.22101211547853, 37.478604425233506]}}, {"type": "Feature", "properties": {}, "geometry": {
        "type": "Polygon", "coordinates": [[[-122.26487159729002, 37.482282467501285], [-122.24324226379393, 37.482282467501285], [-122.24324226379393, 37.49855903614401], [-122.26487159729002, 37.49855903614401], [-122.26487159729002, 37.482282467501285]]]}}]}
]

class TestGeometry(unittest.TestCase):
    def check_bounds(self, json_msg, expected, ep=0):
        f = json_msg['features']
        res = get_geoObjs(f)
        self.assertNotEqual(res, None)
        pt, polys = res
        self.assertEqual(is_in_bounds(pt, polys, ep), expected)
    
    def test_out_of_bounds0(self):
        self.check_bounds(out_of_bounds[0], False)
    
    def test_out_of_bounds1(self):
        self.check_bounds(out_of_bounds[1], False)
    
    def test_in_bounds0(self):
        self.check_bounds(in_bounds[0], True)
    
    def test_in_bounds1(self):
        self.check_bounds(in_bounds[1], True)
    
    def test_depends0_0(self):
        self.check_bounds(depends[0], False)

    def test_depends0_1(self):
        self.check_bounds(depends[0], True, 1e-10)
    
