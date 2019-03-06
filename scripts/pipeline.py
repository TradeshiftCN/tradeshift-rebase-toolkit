import logging
import os
import shutil

import yaml
from colorama import Fore
from git import Repo, NoSuchPathError, GitCommandError, RemoteProgress, BadName
from tqdm import tqdm

import config

LOGGER = logging.getLogger('pipeline')


class Progress(RemoteProgress):
    pbar_dict = dict()
    last_pbar = None

    last_op_code = None
    last_pos = None

    def update(self, op_code, cur_count, max_count=None, message=''):
        op_name = ''
        if op_code == self.COUNTING:
            op_name = "Counting objects"
        elif op_code == self.COMPRESSING:
            op_name = "Compressing objects"
        elif op_code == self.WRITING:
            op_name = "Writing objects"
        elif op_code == self.RECEIVING:
            op_name = 'Receiving objects'
        elif op_code == self.RESOLVING:
            op_name = 'Resolving deltas'
        elif op_code == self.FINDING_SOURCES:
            op_name = 'Finding sources'
        elif op_code == self.CHECKING_OUT:
            op_name = 'Checking out files'

        if op_name:
            if self.last_op_code is None or self.last_op_code != op_code:
                if self.last_pbar is not None:
                    self.last_pbar.close()
                self.last_pbar = tqdm(total=max_count, unit='item', desc=op_name,
                                      bar_format="%s{l_bar}%s%s{bar}%s{r_bar}" %
                                                 (Fore.GREEN, Fore.RESET, Fore.BLUE, Fore.RESET))
                self.last_pos = 0
                self.last_op_code = op_code
            pbar = self.last_pbar
            last_pos = self.last_pos
            diff = cur_count - last_pos
            pbar.update(diff)
            self.last_pbar = pbar
            self.last_op_code = op_code
            self.last_pos = cur_count


class GitHubRepo:
    def __init__(self, work_dir, dir_name, org_name, repo_name):
        self.work_dir = work_dir
        self.dir_name = dir_name
        self.org_name = org_name
        self.repo_name = repo_name
        self.repo = None

    def is_dirty(self):
        return self.repo.is_dirty()

    def get_head_commit_datetime(self):
        return self.repo.head.commit.committed_datetime

    def get_latest_commit_before(self, destination, datetime):
        max_deepth = 5000
        cur_deepth = 50
        while cur_deepth < max_deepth:
            for commit in self.repo.iter_commits(destination, max_count=cur_deepth):
                if commit.committed_datetime < datetime:
                    return commit
            cur_deepth = cur_deepth + 50
        return None

    def clone_tag(self, tag_name):
        try:
            self.repo = Repo(os.path.join(self.work_dir, self.dir_name))
            tag_ref = next((tag for tag in self.repo.tags if tag.commit == self.repo.head.commit), None)
            if tag_ref is not None and tag_ref.name == tag_name:
                LOGGER.warning(f"{tag_name} exists in {self.org_name}/{self.repo_name} , skip cloning.")
            else:
                raise NoSuchPathError()
        except NoSuchPathError as err:
            target_dir = os.path.join(self.work_dir, self.dir_name)
            if os.path.exists(target_dir) and os.path.isdir(target_dir):
                shutil.rmtree(target_dir)
            LOGGER.warning("%s exists, removed, clone again ", target_dir)
            self.repo = Repo.clone_from(url=f'git@github.com:{self.org_name}/{self.repo_name}.git',
                                        to_path=target_dir,
                                        branch=tag_name,
                                        depth=1,
                                        progress=Progress())

    def checkout(self, branch_name):
        self.repo.git.checkout(branch_name)
        return self.repo.active_branch

    def checkout_new_branch(self, base, new_branch_name):
        checkout_name = None
        tags = self.repo.tags
        commit = None
        try:
            commit = self.repo.commit(base)
        except BadName as err:
            # base is not a commit hash
            commit = None
        expected_tag_name = f'v{base}'
        if commit is not None:
            checkout_name = base
        else:
            tag = list(filter(lambda tag: tag.name == f'v{base}', tags))
            if len(tag) == 1:
                checkout_name = expected_tag_name
        if checkout_name is not None:
            self.repo.git.checkout(checkout_name)
            self.repo.create_head(new_branch_name)
        else:
            raise Exception(f'{base} not exist in {self.org_name}/{self.repo_name}')

    def merge_without_commit(self, new_branch):
        try:
            self.repo.git.merge(new_branch)
        except GitCommandError as err:
            if 'Automatic merge failed' in err.stdout:
                LOGGER.error(f'Conflicts are seen in {self.org_name}/{self.repo_name} when merging {new_branch}')
            else:
                LOGGER.error(err)

    def clone(self):
        try:
            self.repo = Repo(os.path.join(self.work_dir, self.dir_name))
            LOGGER.warning("%s exists, skip cloning.", self.dir_name)
        except NoSuchPathError as err:
            LOGGER.info("%s doesn't exist, cloning... it will take a while... ", self.dir_name)
            self.repo = Repo.clone_from(url=f'git@github.com:{self.org_name}/{self.repo_name}.git',
                                        to_path=os.path.join(self.work_dir, self.dir_name),
                                        progress=Progress())

    def add_remote(self, remote_url, remote_name):
        if self.repo:
            try:
                if remote_name in dict((remote.name, remote) for remote in self.repo.remotes):
                    self.repo.delete_remote(remote_name)
                self.repo.create_remote(name=remote_name, url=remote_url)
                LOGGER.info(f'{remote_url} is created as {remote_name} on {self.org_name}/{self.repo_name}.')
            except GitCommandError as err:
                LOGGER.error(err.stdout)
                raise err
        else:
            LOGGER.error(f'{self.org_name}/{self.repo_name} is not cloned yet.')

    def pull(self, branch_name):
        if self.repo:
            self.repo.git.checkout(branch_name)
            self.repo.remotes.origin.pull(branch_name, progress=Progress())
            LOGGER.info(f'{self.org_name}/{self.repo_name}:{branch_name} is pulled.')
        else:
            LOGGER.error(f'{self.org_name}/{self.repo_name} is not cloned yet.')

    def fetch(self, dest):
        if self.repo:
            self.repo.remotes[dest].fetch(progress=Progress())
            LOGGER.info(f'{self.org_name}/{self.repo_name}:{dest} is fetched.')
        else:
            LOGGER.error(f'{self.org_name}/{self.repo_name} is not cloned yet.')


hiera_dir = os.path.join(config.WORKING_DIR, 'hiera')

remote_puppet_repo = GitHubRepo(hiera_dir,
                                config.PUPPET_REPO['upstream']['repo_name'],
                                config.PUPPET_REPO['upstream']['org'],
                                config.PUPPET_REPO['upstream']['repo_name'])
remote_puppet_repo.clone_tag(config.PUPPET_BASELINE_TAG)

remote_puppet_version_file_path = os.path.join(hiera_dir, 'tradeshift-puppet/hiera/versions.yaml')

version_data = dict()
with open(remote_puppet_version_file_path, 'r') as version_file:
    try:
        version_data = yaml.load(version_file)
    except yaml.YAMLError as exc:
        LOGGER.error(exc)
        exit(-1)

# Heracle
# heracle_dir = os.path.join(config.WORKING_DIR, 'heracle')
# for config_name, repo_config in config.HERACLE_REPOS.items():
#     ghrepo = GitHubRepo(heracle_dir, config_name, repo_config['origin']['org'],
#                         repo_config['origin']['repo_name'])
#
#     ghrepo.clone()
#     if not ghrepo.is_dirty():
#         ghrepo.add_remote(
#             remote_url=f'git@github.com:{repo_config["upstream"]["org"]}/{repo_config["upstream"]["repo_name"]}.git',
#             remote_name='upstream')
#         ghrepo.fetch('upstream')
#         hiera_version_key = f"tradeshift::components::{repo_config['hiera-name']}::version"
#         if hiera_version_key in version_data:
#             commit_or_tag = version_data[hiera_version_key]
#             ghrepo.checkout_new_branch(commit_or_tag, config.REBASE_BRANCH_NAME)
#             # target_branch = ghrepo.checkout(repo_config['origin']['branch'])
#             ghrepo.merge_without_commit(f"origin/{repo_config['origin']['branch']}")
#         else:
#             LOGGER.error(f'version.yaml has no version of {config_name}')

# K8s


hiera_commit_datetime = remote_puppet_repo.get_head_commit_datetime()

k8s_dir = os.path.join(config.WORKING_DIR, 'k8s')

for config_name, repo_config in config.K8S_REPOS.items():
    ghrepo = GitHubRepo(k8s_dir, config_name, repo_config['origin']['org'],
                        repo_config['origin']['repo_name'])
    ghrepo.clone()
    if not ghrepo.is_dirty():
        ghrepo.add_remote(
            remote_url=f'git@github.com:{repo_config["upstream"]["org"]}/{repo_config["upstream"]["repo_name"]}.git',
            remote_name='upstream')
        ghrepo.fetch('upstream')
        latest_commit_before_hiera = ghrepo. \
            get_latest_commit_before(f'upstream/{repo_config["upstream"]["branch"]}', hiera_commit_datetime)
        if latest_commit_before_hiera is not None:
            ghrepo.checkout_new_branch(latest_commit_before_hiera.hexsha, config.REBASE_BRANCH_NAME)
            # target_branch = ghrepo.checkout(repo_config['origin']['branch'])
            ghrepo.merge_without_commit(f"origin/{repo_config['origin']['branch']}")
        else:
            LOGGER.error(f'The latest commit before baseline from {config_name} is not found.')
