import argparse 
import time
import getpass

# import requests
# import json 
import threading
from main_logic import poll_and_process

def main():

    
    # get the password 
    if password not in args or:
        args.password = getpass.getpass(f'Password for {args.sender}: ')
    args.password = args.password.encode()

    # get all the client ids 
    with open(args.id_file, 'r') as f:
        client_ids = list(filter(None, f.read().split('\n')))
    
    if args.debug:
        print(time.time(), client_ids)

    while True:
        end_time = time.time() + args.global_step*60
        threads = [threading.Thread(target=poll_and_process, args=(args, i)) for i in client_ids]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        if time.time() < end_time:
            time.sleep(end_time-time.time())
        
if __name__ == "__main__":
    # these args can be transferred all to a config.json file later as the list grows 
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--sender', '-f', help='email used to send from', default='wendyzhang150@gmail.com')
    # parser.add_argument('--password', '-p', help='only for debugging purposes! Program will ask for password if not passed', default='')
    # parser.add_argument('--to', '-to', help='email used to send to', default='qltlws+ducpu0esil3r0@sharklasers.com')
    # parser.add_argument('--API_url', '-api', help='API link', default='https://3qbqr98twd.execute-api.us-west-2.amazonaws.com/test')
    # parser.add_argument('--id_file', '-id', help='file with all the ids where each id is separated by a new line', default='clinicianID.txt')
    # parser.add_argument('--debug', '-d', help='whether to print statements for debugging', action='store_true')
    # parser.add_argument('--timeout', '-t', help='for polling, when it times out (in minutes)', type=float, default=4.0)
    # parser.add_argument('--step', '-s', help='initial steps (in seconds) for polling', type=int, default=10)
    # parser.add_argument('--global_step', '-gs', help='how much time we should give for before launching a new poll (in minutes)', type=int, default=4)
    # args = parser.parse_args()
    main()