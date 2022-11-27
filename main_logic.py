import requests 
import time
from shapely.geometry.polygon import Polygon, Point
import json 
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
import getpass
import numpy as np

def send_individual_email(args, body, subject):
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
        print(time.time, 'Email:', text)
        return 
    while True:
        try:
            s = smtplib.SMTP('smtp.gmail.com', 587)
            # TLS (Transport Layer Security) encrypts all the SMTP commands
            s.starttls()
            s.login(args["sender"], args["password"])
            s.sendmail(args["sender"], args["to"], text)
            s.quit()
            break
        except Exception as e:
            print(e)
            args["password"] = getpass.getpass(f'Password for {args["sender"]} (password may have been typed incorrectly previously): ')

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
    if len(features) != 2:
        return
    f1, f2 = features[0]['geometry'], features[1]['geometry']
    if f1['type'] == 'Point' and f2['type'] == 'Polygon':
        point_coord = f1['coordinates']
        polygon_coord = f2['coordinates']
    elif f1['type'] == 'Polygon' and f2['type'] == 'Point':
        polygon_coord = f1['coordinates']
        point_coord = f2['coordinates']
    else:
        return
    try:
        print('len(polygon_coord)', len(polygon_coord))
        print(polygon_coord)
        point = Point(point_coord)
        poly = Polygon(*polygon_coord)
        return point, poly 
    except Exception as e:
        try:
            point = Point(point_coord)
            poly = Polygon(polygon_coord[0])
            return point, poly
        except Exception as e:
            print('Exception:', e)
            print(polygon_coord)

def send_email(r, okay_msg, in_bounds):
    if okay_msg and in_bounds:
        return 
    if not okay_msg:
        subject = f'[Warning] Endpoint did NOT return expected message for {r.request.path_url}'
        email_body = f"""The endpoint returned the following unexpected message for {r.request.url}:\n{r.text}"""
    elif not in_bounds:
        subject = f'[Warning] Clinician {r.request.path_url} outside of expected range'
        email_body = f"""The clinician location is out of range. The location was requested from {r.request.url}. Here's the whole message returned from the request: \n{r.text}"""

    send_individual_email(args, email_body, subject)

def poll_and_process(args, get_id):
    url = args['API key']+get_id 
    timeout = time.time() + args['timeout']*60
    step_function = lambda s:s*0.9 if s > 1 else s
    timeout = time.time() + timeout
    step = args['step']
    last_r = pt = poly = None
    while True:
        try:
            last_r = requests.get(url)
        except ignore_exceptions as e:
            last_r = e
        if args['debug']:
            print('-'*50)
            print(f'queried {url} at', time.time())
            # print('\t', last_r.text)
        features = get_features(last_r)
        if features:
            geoObjs = get_geoObjs(features)
            if geoObjs:
                pt, poly = geoObjs
                break             

        # Check the time after to make sure the poll function is called at least once
        if  time.time() >= timeout:
            break 

        time.sleep(step)
        if step_function:
            step = step_function(step)
    okay_msg = (pt and poly)
    in_bounds = poly.contains(pt) or poly.touches(pt)
    send_email(last_r, okay_msg, in_bounds)

