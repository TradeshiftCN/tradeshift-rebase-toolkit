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
    "Frontend",
    "Tradeshift-Proxy2",
    "Workflow",
    "p2p-apps",
]

token = token_id = username = password = ''


def my_two_factor_function():
    code = ''
    while not code:
        code = prompt('Enter 2FA code: ')
    return code


# with open('token', 'r') as fd:
#     token = fd.readline().strip()  # Can't hurt to be paranoid
#     token_id = fd.readline().strip()

with open('user', 'r') as fd:
    username = fd.readline().strip()  # Can't hurt to be paranoid
    password = fd.readline().strip()

gh = github3.login(username, password, two_factor_callback=my_two_factor_function)


# auth = gh.authorization(token_id)
# auth.update(add_scopes=['repo:status', 'gist'], rm_scopes=['user'])


def create_pull_request(repo_name):
    print '[%s]creating pull request' % repo_name
    try:
        repository = gh.repository('TradeshiftCN', repo_name)
        repository.create_pull(
            title='sync 12 25',
            base='dev',
            head='TradeshiftCN:sync_12_25',
            body='@Chris-Xie \
                 @yhl10000 ',
        )
    except Exception, e:
        print '[%s]create pull request failed!' % repo_name
        print '     ' + str(e)
    else:
        print '[%s]create pull request successful!' % repo_name


for repo_name in repos:
    create_pull_request(repo_name)
