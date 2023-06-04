import time
import webbrowser
from auth0.authentication.token_verifier import TokenVerifier, AsymmetricSignatureVerifier
import auth0.authentication as auth
import auth0 as auth0
import jwt

import requests

import data_structures as ds
AUTH0_DOMAIN = 'dev-xb2pdakilxx5fa3q.us.auth0.com'
AUTH0_CLIENT_ID = 'X9TA1vRkwFrxUrWavl6Pt7WkyNdQMqZM'
ALGORITHMS = ['RS256']

current_user = None


def validate_token(id_token):
    """
    Verify the token and its precedence

    :param id_token:
    """
    jwks_url = 'https://{}/.well-known/jwks.json'.format(AUTH0_DOMAIN)
    issuer = 'https://{}/'.format(AUTH0_DOMAIN)
    sv = AsymmetricSignatureVerifier(jwks_url)
    tv = TokenVerifier(signature_verifier=sv, issuer=issuer, audience=AUTH0_CLIENT_ID)
    tv.verify(id_token)


def sign_up():
    webbrowser.open(f'https://dev-xb2pdakilxx5fa3q.us.auth0.com/authorize?response_type=code|token&client_id=X9TA1vRkwFrxUrWavl6Pt7WkyNdQMqZM&redirect_uri=https://wikipedia.org&screen_hint=sign_up&prompt=login')

def login():
    """
    Runs the device authorization flow and stores the user object in memory
    """
    device_code_payload = {
        'client_id': AUTH0_CLIENT_ID,
        'scope': 'openid profile'
    }
    try: device_code_response = requests.post('https://{}/oauth/device/code'.format(AUTH0_DOMAIN), data=device_code_payload)
    except:
        raise ConnectionError('We experienced an error connecting to the Auth0 server')

    if device_code_response.status_code != 200:
        raise ConnectionError('We experienced an error generating the device code')

    device_code_data = device_code_response.json()
    yield device_code_data['user_code']
    yield device_code_data['verification_uri_complete']


    token_payload = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
        'device_code': device_code_data['device_code'],
        'client_id': AUTH0_CLIENT_ID
    }

    authenticated = False
    while not authenticated:
        token_response = requests.post('https://{}/oauth/token'.format(AUTH0_DOMAIN), data=token_payload)

        token_data = token_response.json()
        if token_response.status_code == 200:

            validate_token(token_data['id_token'])
            global current_user
            current_user = jwt.decode(token_data['id_token'], algorithms=ALGORITHMS,
                                      options={"verify_signature": False})
            yield current_user
            authenticated = True
        elif token_data['error'] not in ('authorization_pending', 'slow_down'):
            raise ConnectionError('It seems like something went wrong with the login.')

        else:
            time.sleep(device_code_data['interval'])

def logout():
    return f'https://{AUTH0_DOMAIN}/oidc/logout'

def say_hi():
    if current_user is None:
        for _ in login(): pass
    print("HII!!")
    print(f"Welcome {current_user['nickname']}!")
    return ds.deobjectify(current_user)

if __name__ == '__main__':
    for i in range(1):
        print(logout())
        #current_user = None
        #new_items = say_hi()
        #if i == 0: shared_items = dict(new_items)
        #shared_items = {k: shared_items[k] for k in shared_items if new_items[k] == shared_items[k]}
    #print(shared_items)