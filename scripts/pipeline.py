import logging
import os
import sys

import yaml

import config
from utils import GitHubRepo

LOGGER = logging.getLogger('pipeline')


def parse_puppet_for_heracle(workdir, puppet_repo_config, baseline_tag):
    puppet_repo = GitHubRepo(workdir,
                             puppet_repo_config['upstream']['repo_name'],
                             puppet_repo_config['upstream']['org'],
                             puppet_repo_config['upstream']['repo_name'])
    puppet_repo.fetch(dest='origin', tag=baseline_tag)
    puppet_repo.checkout(baseline_tag)
    puppet_version_file_path = os.path.join(workdir,
                                            f'{puppet_repo_config["upstream"]["repo_name"]}/hiera/versions.yaml')

    version_dict = dict()
    with open(puppet_version_file_path, 'r') as version_file:
        try:
            version_dict = yaml.safe_load(version_file)
        except yaml.YAMLError as exc:
            LOGGER.error(exc)
            raise exc

    hiera_commit_datetime = puppet_repo.get_head_commit_datetime()
    return version_dict, hiera_commit_datetime


def clone_and_merge_versioned(workdir, repo_configs, version_dict):
    for config_name, repo_configs in repo_configs.items():
        ghrepo = GitHubRepo(workdir,
                            config_name,
                            repo_configs['origin']['org'],
                            repo_configs['origin']['repo_name'])
        ghrepo.fetch(dest='origin', branch_name=repo_configs['origin']['branch'])
        if not ghrepo.is_dirty():
            ghrepo.add_remote(
                remote_url=(f'git@github.com:{repo_configs["upstream"]["org"]}/'
                            f'{repo_configs["upstream"]["repo_name"]}.git'),
                remote_name='upstream')
            hiera_version_key = f"tradeshift::components::{repo_configs['hiera-name']}::version"
            if hiera_version_key in version_dict:
                commit_or_tag = version_dict[hiera_version_key]

                ghrepo.fetch(dest='upstream')
                ghrepo.checkout_new_branch(commit_or_tag, config.REBASE_BRANCH_NAME)
                ghrepo.merge_without_commit(f"origin/{repo_configs['origin']['branch']}")
            else:
                LOGGER.error(f'version.yaml has no version of {config_name}')
        else:
            LOGGER.error(f'{config_name} is dirty, skip.')


def clone_and_merge_timed(workdir, repo_configs, lastest_before):
    for config_name, repo_config in repo_configs.items():
        ghrepo = GitHubRepo(workdir, config_name, repo_config['origin']['org'], repo_config['origin']['repo_name'])
        ghrepo.fetch(dest='origin', branch_name=repo_configs['origin']['branch'])
        if not ghrepo.is_dirty():
            ghrepo.add_remote(
                remote_url=(f'git@github.com:{repo_config["upstream"]["org"]}/'
                            f'{repo_config["upstream"]["repo_name"]}.git'),
                remote_name='upstream')
            ghrepo.fetch(dest='upstream')
            latest_commit_before_hiera = \
                ghrepo.get_latest_merge_commit_before(f'upstream/{repo_config["upstream"]["branch"]}', lastest_before)
            if latest_commit_before_hiera is not None:
                ghrepo.checkout_new_branch(latest_commit_before_hiera.hexsha, config.REBASE_BRANCH_NAME)
                # target_branch = ghrepo.checkout(repo_config['origin']['branch'])
                ghrepo.merge_without_commit(f"origin/{repo_config['origin']['branch']}")
            else:
                LOGGER.error(f'The latest commit before baseline from {config_name} is not found.')
        else:
            LOGGER.error(f'{config_name} is dirty, skip.')


def main(*args):
    hiera_dir = os.path.join(config.WORKING_DIR, 'hiera')
    (version_dict, commit_datetime) = parse_puppet_for_heracle(hiera_dir, config.PUPPET_REPO,
                                                               config.PUPPET_BASELINE_TAG)
    heracle_dir = os.path.join(config.WORKING_DIR, 'heracle')
    clone_and_merge_versioned(heracle_dir, config.HERACLE_REPOS, version_dict)

    k8s_dir = os.path.join(config.WORKING_DIR, 'k8s')
    clone_and_merge_timed(k8s_dir, config.K8S_REPOS, commit_datetime)

    it_dir = os.path.join(config.WORKING_DIR, 'it')
    clone_and_merge_timed(it_dir, config.IT_REPOS, commit_datetime)


if __name__ == '__main__':
    main(*sys.argv[1:])
