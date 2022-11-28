import requests 
import time
from shapely.geometry.polygon import Polygon, Point
import json 
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from copy import deepcopy
from math import inf 

def send_email(args, body, subject):
    """ 
    sends an email 

    :param args: should have the fields: sender, to, password, debug 
    :param body: email body message 
    :param subject: email subject  
    """
    # set up message 
    msg = MIMEMultipart()
    msg['From'] = args["sender"]
    msg['To'] = args["to"]
    msg['Subject'] = subject
    msg.attach(MIMEText(body, "plain"))
    text = msg.as_string()
    if args['debug']:
        print('\x1b[6;30;42m%sm %s \x1b[0m' % ('Email:', text))
    
    # trying to send the email 
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        # TLS (Transport Layer Security) encrypts all the SMTP commands
        s.starttls()
        s.login(args["sender"], deepcopy(args["password"]))
        s.sendmail(args["sender"], args["to"], text)
        s.quit()
        return True 
    except Exception as e:
        print('Email Exception:', e)
        return False 

def create_and_send_email(args, r, has_exception, okay_msg=False, in_bounds=False):
    '''
    Judges if we should send a warning email 
    returns bool that tells us whether we sent an email or not 

    :param args: args must have fields expected for `send_email` function 
    :param r: the reponse or the expection thrown 
    :has_exception: whether there was an exception
    :param okay_msg: whether the request was okay and the request body was what we expected 
    :param in_bounds: whether the clnician was in bounds 
    '''
    if okay_msg and in_bounds and not has_exception:
        return False 
    if has_exception:
        subject = f'[Warning] No valid response for {r[0]}'
        email_body = f"""We did not get a valid response when querying for {r[0]}. Here is the exception: {r[1]}"""
    if not okay_msg:
        subject = f'[Warning] Endpoint did NOT return expected message for {r.request.path_url}'
        email_body = f"""The endpoint returned the following unexpected message for {r.request.url}:\n{r.text}"""
    elif not in_bounds:
        subject = f'[Warning] Clinician {r.request.path_url} outside of expected range'
        email_body = f"""The clinician location is out of range. The location was requested from {r.request.url}. Here's the whole message returned from the request: \n{r.text}\nUse https://geojson.io/ to see the map location"""
    return send_email(args, email_body, subject)

def get_features(request):
    '''
    checks if we have a valid request and if the request body is json and has a features field 
    returns either nothing or the features field 

    '''
    if request.status_code >= 300:
        return
    try:
        json_msg = json.loads(request.text)
    except ValueError as e:
        return
    if 'features' not in json_msg:
        return
    return json_msg['features']

def get_geoObjs(features):
    '''
    Returns 1 point and a list of polygons based on a list of features 

    If no features or more than 1 point in the list or no polygons in list, return nothing
    '''
    if not features:
        return 
    pts_coord = []
    poly_coords = []
    for f in features:
        if f['geometry']['type'] == 'Point':
            pts_coord.append(f['geometry']['coordinates'])
        elif f['geometry']['type'] == 'Polygon':
            poly_coords.append(f['geometry']['coordinates'])
    if len(pts_coord) != 1 or len(poly_coords) == 0:       
        # return if we have more 1 pt or if no polygons were given  
        return 
    
    point = Point(pts_coord[0])
    polys = []
    for polygon_coord in poly_coords:
        try:
            polys.append(Polygon(*polygon_coord))
        except Exception as e:
            try:
                polys.extend([Polygon(poly) for poly in polygon_coord])
            except Exception as e:
                print('Exception:', e)
                print(polygon_coord)
    return point, polys

def is_in_bounds(pt, polys, ep):
    '''
    returns True if pt within one of polygons or within ep distance from a polygon's boundary

    :param pt: point (shapely object)
    :param polys: list of polygons (shapely objects)
    :param ep: epsilon/allowance distance (float)
    '''
    for p in polys:
        if p.boundary.distance(pt) < ep or pt.within(p) or pt.touches(p):
            return True 
    return False 

def poll_and_process(args, get_id):
    '''
    Given the get_id and the API url in args,  
    '''
    url = args['API url']+get_id 
    step_function = None #lambda s:s*0.9 if s > 1 else s
    step = args['query step']
    last_r = pt = polys = None
    print_n = 0 
    while True:
        stop_time = time.time() + step
        has_exception = False 
        # get request 
        try:
            last_r = requests.get(url)
        except Exception as e:
            last_r = (get_id, e)
            print(e)
            has_exception = True 
        
        # check if it's a valid response  
        if not has_exception:
            features = get_features(last_r)
            geoObjs = get_geoObjs(features)
            okay_msg = (features and geoObjs)
            in_bounds = False 
        if not has_exception and geoObjs:
            pt, polys = geoObjs
            in_bounds = is_in_bounds(pt, polys, args['epsilon'])  
        sent = create_and_send_email(args, last_r, has_exception, okay_msg, in_bounds)
        if sent:
            if args['debug']:
                print('-'*50)
                print(f'\x1b[6;30;42mSent warning for {url} at', time.time(),'\x1b[0m')
            step = args['query step']
            time.sleep(args['wait']*60)
        else:
            if args['debug'] and print_n%20 == 0:
                print('-'*50)
                print(f'queried {url} at', time.time())     
                print('\t', last_r.text)
            if stop_time > time.time():
                time.sleep(stop_time-time.time())
            if step_function:
                step = step_function(step)
        print_n += 1

