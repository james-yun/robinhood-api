import json
import requests
import getpass

session = requests.Session()


def oauth(payload):
    global session

    url = 'https://api.robinhood.com/oauth2/token/'
    r = session.post(url, json=payload)
    session.headers.pop('challenge_id', None)
    response = r.json()

    if 'access_token' in response:
        # save bearer_token and write to tokens.json
        session.headers['Authorization'] = 'Bearer ' + response['access_token']
        with open('tokens.json', 'w') as file:
            file.write(json.dumps({
                'bearer_token': response['access_token'],
                'refresh_token': response['refresh_token'],
                'device_token': payload['device_token']
            }))

    return r


def login(username=None, password=None, device_token='c77a7142-cc14-4bc0-a0ea-bdc9a2bf6e68'):
    """generates OAuth2 bearer token"""
    global session

    # check if bearer token exists and is valid
    with open('tokens.json') as file:
        tokens = json.loads(file.read())
        if 'bearer_token' in tokens:
            session.headers['Authorization'] = 'Bearer ' + tokens['bearer_token']
            if user():
                return
            else:
                del session.headers['Authorization']

    if username is None:
        username = input('Enter email or username: ')
    if password is None:
        password = getpass.getpass('Enter password: ')

    payload = {
        'grant_type': 'password',
        'scope': 'internal',
        'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
        'expires_in': 86400,
        'device_token': device_token,
        'username': username,
        'password': password
    }

    r = oauth(payload)
    print('login: ')
    if r.status_code == 400 or r.status_code == 401:
        # 400: incorrect credentials or unfamiliar device token
        print(r.text)
        if r.json()['detail'] == 'Request blocked, challenge type required.':
            challenge_type = None
            while challenge_type != 1 and challenge_type != 2:
                challenge_type = int(input("\nWe're sending you a code to verify your login. Do you want us to:\n"
                                           "  1: Text you the code\n"
                                           "  2: Email it to you?\n"))
                if challenge_type == 1:
                    print('Texting...')
                    payload['challenge_type'] = 'sms'
                elif challenge_type == 2:
                    print('Emailing...')
                    payload['challenge_type'] = 'email'
            r = oauth(payload)
            del payload['challenge_type']
            challenge_id = r.json()['challenge']['id']
            verification_code = input('Enter your verification code: ')
            url = f'https://api.robinhood.com/challenge/{challenge_id}/respond/'
            r = session.post(url, json={'response': verification_code})
            print(r.text)
            session.headers['X-ROBINHOOD-CHALLENGE-RESPONSE-ID'] = challenge_id
            r = oauth(payload)
            del session.headers['X-ROBINHOOD-CHALLENGE-RESPONSE-ID']
    user()


def user():
    """checks whether user is logged in"""
    url = "https://api.robinhood.com/user/"
    r = session.get(url)
    if r.status_code == 401:
        # invalid bearer token
        return False
    else:
        print(f"Logged in as {r.json()['profile_name']}.\n")
        return True


def account():
    url = 'https://api.robinhood.com/accounts/'
    r = session.get(url)
    print(r.text)
    return r.json()['results'][0]


def positions():
    url = 'https://api.robinhood.com/positions/?nonzero=true'
    r = session.get(url)
    if r.status_code == 401:
        raise Exception(r.text + '\nYour bearer_token may have expired. You can generate a new one in authenticate.py')
    r = r.json()
    positions = {}
    for result in r['results']:
        instrument = result['instrument']
        r = session.get(instrument).json()
        positions[r['symbol']] = {
            'quantity': result['quantity'],
            'average_buy_price': result['average_buy_price']
        }
    return positions