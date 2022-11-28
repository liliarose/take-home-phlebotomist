import requests 
import time
from shapely.geometry.polygon import Polygon, Point
import json 
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
import getpass
from copy import deepcopy
from math import inf 
import numpy as np 

def send_email(args, body, subject):
    """ 
    :param sender: email and password of the sender 

    sender, msg, subject should all be strings recipients should be lists of emails just in case we want to send to multiple ppl 
    """
    msg = MIMEMultipart()
    msg['From'] = args["sender"]
    msg['To'] = args["to"]
    msg['Subject'] = subject
    msg.attach(MIMEText(body, "plain"))
    text = msg.as_string()
    if args['debug']:
        print('\x1b[%sm %s \x1b[0m' % ('Email:', text))
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

def create_and_send_email(args, r, okay_msg, in_bounds):
    if okay_msg and in_bounds:
        return 
    if not okay_msg:
        subject = f'[Warning] Endpoint did NOT return expected message for {r.request.path_url}'
        email_body = f"""The endpoint returned the following unexpected message for {r.request.url}:\n{r.text}"""
    elif not in_bounds:
        subject = f'[Warning] Clinician {r.request.path_url} outside of expected range'
        email_body = f"""The clinician location is out of range. The location was requested from {r.request.url}. Here's the whole message returned from the request: \n{r.text}\nUse https://geojson.io/ to see the map location"""
    return send_email(args, email_body, subject)

def get_features(request):
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
    for p in polys:
        if p.boundary.distance(pt) < ep or pt.within(p) or pt.touches(p):
            return True 
    return False 

def poll_and_process(args, get_id):
    url = args['API url']+get_id 
    timeout = time.time() + args['timeout']*60
    step_function = lambda s:s*0.9 if s > 1 else s
    timeout = time.time() + timeout
    step = args['query step']
    max_tries = args.get('max tries', inf)
    last_r = pt = polys = None
    tries = 0 
    while tries < max_tries:
        try:
            last_r = requests.get(url)
        except ignore_exceptions as e:
            last_r = e
        tries += 1
        features = get_features(last_r)
        if features:
            geoObjs = get_geoObjs(features)
            if geoObjs:
                pt, polys = geoObjs
                break      

        if args['debug']:
            print('-'*50)
            print(f'queried {url} at', time.time())     
            print('\t', last_r.text)
        # break only after we've queried at least once 
        if  time.time() >= timeout:
            break 
        time.sleep(step)
        if step_function:
            step = step_function(step)
    if args['debug']:
        print('-'*50)
        print(f'\x1b[6;30;42mfinished querying {url} at', time.time(),'\x1b[0m')
        print('\t', last_r.text)
    okay_msg = (pt and polys)
    in_bounds = False 
    if okay_msg:
        ep = args['epsilon']
        in_bounds = is_in_bounds(pt, polys, ep)
    return create_and_send_email(args, last_r, okay_msg, in_bounds)

