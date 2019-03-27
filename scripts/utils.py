#!/usr/bin/env python  
""" 
@author:shz 
@license: Apache Licence 
@file: utils.py 
@time: 2019/03/15
@contact: sunhouzan@163.com
@site:  
@software: PyCharm 
"""

import logging
import os
import shutil

from colorama import Fore
from git import Repo, NoSuchPathError, GitCommandError, RemoteProgress, BadName
from tqdm import tqdm


class TqdmHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class Progress(RemoteProgress):
    pbar_dict = dict()
    last_pbar = None

    last_op_code = None
    last_pos = None
    op_names = {RemoteProgress.COUNTING: 'Counting objects',
                RemoteProgress.COMPRESSING: 'Compressing objects',
                RemoteProgress.WRITING: 'Writing objects',
                RemoteProgress.RECEIVING: 'Receiving objects',
                RemoteProgress.RESOLVING: 'Resolving deltas',
                RemoteProgress.FINDING_SOURCES: 'Finding sources',
                RemoteProgress.CHECKING_OUT: 'Checking out files'}
    max_msg_len = 0
    for i, (key, value) in enumerate(op_names.items()):
        if len(value) > max_msg_len:
            max_msg_len = len(value)
    for i, (key, value) in enumerate(op_names.items()):
        if len(value) < max_msg_len:
            appended_value = value + (' ' * (max_msg_len - len(value)))
            op_names[key] = appended_value

    def update(self, op_code, cur_count, max_count=None, message=''):
        if op_code in self.op_names:
            op_name = self.op_names[op_code]
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
    LOGGER = logging.getLogger('GitHubRepo')

    def __init__(self, work_dir, dir_name, org_name, repo_name, ):
        self.work_dir = work_dir
        self.dir_name = dir_name
        self.org_name = org_name
        self.repo_name = repo_name
        try:
            self.repo = Repo(os.path.join(self.work_dir, self.dir_name))
        except NoSuchPathError as err:
            self.LOGGER.info(f'{org_name}/{repo_name} not exist, creating...')
            self.repo = Repo.init(path=os.path.join(self.work_dir, self.dir_name))
            self.add_remote(remote_url=f'git@github.com:{self.org_name}/{self.repo_name}.git',
                            remote_name='origin')

    def is_dirty(self):
        return self.repo.is_dirty()

    def get_head_commit_datetime(self):
        return self.repo.head.commit.committed_datetime

    def get_latest_merge_commit_before(self, destination, datetime):
        max_deepth = 5000
        cur_deepth = 50
        while cur_deepth < max_deepth:
            for commit in self.repo.iter_commits(destination, max_count=cur_deepth, merges=True):
                if commit.committed_datetime < datetime:
                    return commit
            cur_deepth = cur_deepth + 50
        return None

    def checkout_tag(self, dest: str, tag_name: str):
        tag_ref = next((tag for tag in self.repo.tags if tag.commit == self.repo.head.commit), None)
        if tag_ref is not None and tag_ref.name == tag_name:
            self.LOGGER.warning(f"{tag_name} exists in {self.org_name}/{self.repo_name} , skip cloning.")
        else:
            self.fetch(dest, tag_name)

    def clone_tag(self, tag_name):
        try:
            self.repo = Repo(os.path.join(self.work_dir, self.dir_name))
            tag_ref = next((tag for tag in self.repo.tags if tag.commit == self.repo.head.commit), None)
            if tag_ref is not None and tag_ref.name == tag_name:
                self.LOGGER.warning(f"{tag_name} exists in {self.org_name}/{self.repo_name} , skip cloning.")
            else:
                raise NoSuchPathError()
        except NoSuchPathError as err:
            target_dir = os.path.join(self.work_dir, self.dir_name)
            if os.path.exists(target_dir) and os.path.isdir(target_dir):
                shutil.rmtree(target_dir)
            self.LOGGER.warning("%s exists, removed, clone again ", target_dir)
            self.repo = Repo.clone_from(url=f'git@github.com:{self.org_name}/{self.repo_name}.git',
                                        to_path=target_dir,
                                        branch=tag_name,
                                        depth=1,
                                        progress=Progress())

    def checkout(self, branch_name):
        self.repo.git.checkout(branch_name)
        if self.repo.head.is_detached:
            return next((tag for tag in self.repo.tags if tag.commit == self.repo.head.commit),
                        self.repo.head.commit.hexsha)
        else:
            return self.repo.active_branch

    def checkout_new_branch(self, base_commit_or_tag, new_branch_name):
        checkout_name = None
        tags = self.repo.tags
        try:
            commit = self.repo.commit(base_commit_or_tag)
            if commit:
                checkout_name = base_commit_or_tag
        except BadName as err:
            # base is not a commit hash
            expected_tag_name = f'v{base_commit_or_tag}'
            tag = list(filter(lambda tag: tag.name == expected_tag_name, tags))
            if len(tag) == 1:
                checkout_name = expected_tag_name

        if checkout_name is not None:
            self.repo.git.checkout(checkout_name)
            self.repo.create_head(new_branch_name)
            self.repo.git.checkout(new_branch_name)
        else:
            raise Exception(f'{base_commit_or_tag} not exist in {self.org_name}/{self.repo_name}')

    def merge_without_commit(self, new_branch):
        try:
            self.repo.git.merge(new_branch)
        except GitCommandError as err:
            if 'Automatic merge failed' in err.stdout:
                self.LOGGER.error(f'Conflicts are seen in {self.org_name}/{self.repo_name} when merging {new_branch}')
                for err_line in filter(lambda line: 'CONFLICT' in line, err.stdout.split('\n')):
                    self.LOGGER.error(err_line)
            else:
                self.LOGGER.error(err)

    def clone(self):
        try:
            self.repo = Repo(os.path.join(self.work_dir, self.dir_name))
            self.LOGGER.warning("%s exists, skip cloning.", self.dir_name)
        except NoSuchPathError as err:
            self.LOGGER.info("%s doesn't exist, cloning... it will take a while... ", self.dir_name)
            self.repo = Repo.clone_from(url=f'git@github.com:{self.org_name}/{self.repo_name}.git',
                                        to_path=os.path.join(self.work_dir, self.dir_name),
                                        progress=Progress())

    def add_remote(self, remote_url, remote_name):
        if self.repo:
            try:
                if remote_name in dict((remote.name, remote) for remote in self.repo.remotes):
                    self.repo.delete_remote(remote_name)
                self.repo.create_remote(name=remote_name, url=remote_url)
                self.LOGGER.info(f'{remote_url} is created as {remote_name} on {self.org_name}/{self.repo_name}.')
            except GitCommandError as err:
                self.LOGGER.error(err.stdout)
                raise err
        else:
            self.LOGGER.error(f'{self.org_name}/{self.repo_name} is not cloned yet.')

    def pull(self, branch_name):
        if self.repo:
            self.repo.git.checkout(branch_name)
            self.repo.remotes.origin.pull(branch_name, progress=Progress())
            self.LOGGER.info(f'{self.org_name}/{self.repo_name}:{branch_name} is pulled.')
        else:
            self.LOGGER.error(f'{self.org_name}/{self.repo_name} is not cloned yet.')

    def fetch(self, dest: str, depth: int = None, branch_name: str = None, tag: str = None):
        if branch_name:
            ref_spec = branch_name
        else:
            ref_spec = f'+refs/tags/{tag}:refs/tags/{tag}' if tag else None
        if depth:
            self.repo.remotes[dest].fetch(refspec=ref_spec, depth=depth, progress=Progress())
        else:
            self.repo.remotes[dest].fetch(refspec=ref_spec, progress=Progress())
        self.LOGGER.info(f'{self.org_name}/{self.repo_name}:{dest} is fetched.')
