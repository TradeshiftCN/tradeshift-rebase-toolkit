#!/usr/bin/env python
# Deprecated
from getpass import getuser, getpass

from github3 import authorize

try:
    # Python 2
    prompt = raw_input
except NameError:
    # Python 3
    prompt = input


def my_two_factor_callback():
    auth_code = raw_input('Please enter your 2FA code: ')
    return auth_code


user = prompt('Enter username: ')
password = ''

while not password:
    password = getpass('Password for {0}: '.format(user))

note = 'tradeshift-rebase-toolkit'
note_url = 'https://cn-sandbox.tradeshift.com'
scopes = ['user', 'repo']

auth = authorize(user, password, scopes, note, note_url, two_factor_callback=my_two_factor_callback)

with open('token', 'w') as fd:
    fd.write(auth.token + '\n')
    fd.write(str(auth.id))
