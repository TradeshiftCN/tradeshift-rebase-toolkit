#!/usr/bin/env python

from getpass import getuser, getpass

import github3

try:
    # Python 2
    prompt = raw_input
except NameError:
    # Python 3
    prompt = input

repos = [
    "Apps",
    "App-Service",
    "Backend-Service",
    "tradeshift-product-engine",
    "tradeshift-company-profile",
    "Frontend",
    "Tradeshift-Proxy2",
    "Workflow",
    "p2p-apps",
]

# use username password, two phase authentication code is required
username = ''
password = ''
branch = ''

code = ''
def my_two_factor_function():
    global code
    while not code:
        code = prompt('Enter 2FA code: ')
    return code

while not username:
    username = prompt('Enter username: ')

while not password:
    password = getpass('Enter password: ')

gh = github3.login(username, password, two_factor_callback=my_two_factor_function)


# use token (not working cause https://github.com/sigmavirus24/github3.py/issues/602)
# token = token_id = ''

# with open('token', 'r') as fd:
#     token = fd.readline().strip()  # Can't hurt to be paranoid
#     token_id = fd.readline().strip()

# gh = github3.login(token=token)
# auth = gh.authorization(token_id)
# auth.update(add_scopes=['repo:status', 'gist'], rm_scopes=['user'])


while not branch:
    branch = prompt('Enter rebase branch: ')

def create_pull_request(repo_name):
    print '[%s]creating pull request' % repo_name
    try:
        repository = gh.repository('TradeshiftCN', repo_name)
        repository.create_pull(
            title=branch,
            base='dev-stable',
            head='TradeshiftCN:' + branch,
            body='@Chris-Xie ',
        )
    except Exception, e:
        print '[%s]create pull request failed! Please check if the branch is exsits or the PR is created.' % repo_name
        print '     ' + str(e)
    else:
        print '[%s]create pull request successful!' % repo_name


for repo_name in repos:
    create_pull_request(repo_name)
