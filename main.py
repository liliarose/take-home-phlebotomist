import argparse
import time
import getpass
import json
import threading
from main_logic import poll_and_process

required_config_keys = {'sender', 'to', 'API url',
                        'id_file', 'wait', 'query step', 'epsilon'}


def main(cl_args):
    with open('configs.json', 'r') as f:
        args = json.load(f)
    diff = required_config_keys- set(args.keys())
    if diff:
        raise Exception('Missing the following configurations:', ', '.join(diff))

    args['debug'] = cl_args
    # get the password
    if 'password' not in args or not args['password']:
        args['password'] = getpass.getpass(f'Password for {args["sender"]}: ')
    args['password'] = args['password']

    # get all the client ids
    with open(args['id_file'], 'r') as f:
        client_ids = list(filter(None, f.read().split('\n')))

    if args['debug']:
        print(time.time(), client_ids)
    
    threads = [threading.Thread(target=poll_and_process, args=(args, i)) for i in client_ids]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--debug', '-d', help='whether to print statements for debugging', action='store_true')
    args = parser.parse_args()
    main(args)
