from getpass import getuser, getpass

from github3 import authorize


def my_two_factor_callback():
    auth_code = raw_input('Please enter your 2FA code: ')
    return auth_code


user = getuser()
password = ''

while not password:
    password = getpass('Password for {0}: '.format(user))

note = 'github3.py example app'
note_url = 'http://example.com'
scopes = ['user', 'repo']

auth = authorize(user, password, scopes, note, note_url, two_factor_callback=my_two_factor_callback)

with open('token', 'w') as fd:
    fd.write(auth.token + '\n')
    fd.write(str(auth.id))
