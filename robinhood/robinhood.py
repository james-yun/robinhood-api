import json
import requests
import getpass

session = requests.Session()
account_url = None


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
        try:
            tokens = json.loads(file.read())
            if 'bearer_token' in tokens:
                session.headers['Authorization'] = 'Bearer ' + tokens['bearer_token']
                if user():
                    return
                else:
                    del session.headers['Authorization']
        except json.decoder.JSONDecodeError:
            pass

    if username is None:
        username = input('Enter email or username: ')
    if password is None:
        password = getpass.getpass('Enter password: ')

    payload = {
        'grant_type': 'password',
        'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
        'device_token': device_token,
        'username': username,
        'password': password
    }

    r = oauth(payload)
    if r.status_code == 400:
        if r.json()['detail'] == 'Request blocked, challenge type required.':
            challenge_type = None
            while challenge_type not in ['1', '2']:
                print('Unfamiliar device detected.')
                challenge_type = input("We're sending you a code to verify your login. Do you want us to:\n"
                                       "  1: Text you the code\n"
                                       "  2: Email it to you?\n")
                if challenge_type == '1':
                    print('Texting...')
                    payload['challenge_type'] = 'sms'
                elif challenge_type == '2':
                    print('Emailing...')
                    payload['challenge_type'] = 'email'
            r = oauth(payload)
            del payload['challenge_type']
            challenge_id = r.json()['challenge']['id']
            url = f'https://api.robinhood.com/challenge/{challenge_id}/respond/'
            verified = False
            while verified is False:
                verification_code = input('\nEnter your verification code: ')
                r = session.post(url, json={'response': verification_code}).json()
                if 'id' in r:
                    verified = True
                    print('\nVerified device.\n')
                else:
                    remaining_attempts = r['challenge']['remaining_attempts']
                    if remaining_attempts > 0:
                        print(f"Code is invalid. Remaining attempts: {remaining_attempts}.")
                    else:
                        raise RuntimeError('Verification failed.')
            session.headers['X-ROBINHOOD-CHALLENGE-RESPONSE-ID'] = challenge_id
            oauth(payload)
            del session.headers['X-ROBINHOOD-CHALLENGE-RESPONSE-ID']
        else:
            raise RuntimeError('Unable to log in with provided credentials.')
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


def accounts():
    global account_url
    url = 'https://api.robinhood.com/accounts/'
    r = session.get(url).json()
    account_url = r['results'][0]['url']
    return r['results'][0]


def instruments(instrument=None, symbol=None):
    url = 'https://api.robinhood.com/instruments/'
    if instrument is not None:
        url += f'{instrument}/'
    if symbol is not None:
        url += f'?symbol={symbol}'
    r = session.get(url)
    return r.json()


def positions():
    url = 'https://api.robinhood.com/positions/?nonzero=true'
    r = session.get(url)
    if r.status_code == 401:
        raise Exception(r.text + '\nYour bearer_token may have expired. You can generate a new one in authenticate.py')
    r = r.json()
    positions = {}
    for result in r['results']:
        instrument_url = result['instrument']
        r = session.get(instrument_url).json()
        positions[r['symbol']] = {
            'quantity': result['quantity'],
            'average_buy_price': result['average_buy_price']
        }
    return positions


def fundamentals(instrument):
    url = f'https://api.robinhood.com/fundamentals/{instrument.upper()}/'
    r = session.get(url)
    return r.json()


def quotes(instrument):
    url = f'https://api.robinhood.com/marketdata/quotes/{instrument.upper()}/'
    r = session.get(url)
    return r.json()


def orders(price, symbol, instrument=None, quantity=1, type='market', side='buy', time_in_force='gfd',
           trigger='immediate', account=None):
    global account_url
    if account is None:
        account = account_url
    if instrument is None:
        instrument = fundamentals(symbol)['instrument']
    url = 'https://api.robinhood.com/orders/'
    r = session.post(url, json=locals())
    return r.json()
