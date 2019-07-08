import logging
import os

from coloredlogs import ColoredFormatter

from utils import TqdmHandler

LOGFORMAT = '%(name)s - %(levelname)s - %(message)s'
formatter = ColoredFormatter(LOGFORMAT)
stream = TqdmHandler()
stream.setLevel(logging.INFO)
stream.setFormatter(formatter)

logging.basicConfig(level=logging.INFO,
                    format=LOGFORMAT,
                    handlers=[stream])

# =========================== Modify Following ===========================

# Create your private token here https://github.com/settings/tokens
GITHUB_TOKEN = 'token'

# Example: os.path.expanduser('~/TradeshiftCN/rebase/')
WORKING_DIR = 'change this'

# Example: 'procution-6265'
PUPPET_BASELINE_TAG = 'change this'
# Example: 'rebase-2019-03-04'
REBASE_BRANCH_NAME = 'change this'

PUPPET_REPO = {
    'origin': {
        'org': 'TradeshiftCN',
        'repo_name': 'tradeshift-puppet',
        'branch': 'testing'
    },
    'upstream': {
        'org': 'Tradeshift',
        'repo_name': 'tradeshift-puppet',
        'branch': 'master'
    }
}

HERACLE_REPOS = {
    'App-Service': {
        'hiera-name': 'tradeshift_app_backend',
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'App-Service',
            'branch': 'dev-stable'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'App-Service',
        }
    },
    'Apps': {
        'hiera-name': 'tradeshift_v4_apps',
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'Apps',
            'branch': 'dev-stable'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'Apps',
        }
    },
    'Backend-Service': {
        'hiera-name': 'tradeshift_backend',
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'Backend-Service',
            'branch': 'dev-stable'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'Backend-Service',
        }
    },
    'Frontend': {
        'hiera-name': 'frontend',
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'Frontend',
            'branch': 'dev-stable'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'Frontend',
        }
    },
    'Tradeshift-Proxy2': {
        'hiera-name': 'tradeshift_proxy',
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'Tradeshift-Proxy2',
            'branch': 'dev-stable'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'Tradeshift-Proxy2',
        }
    },
    'tradeshift-product-engine': {
        'hiera-name': 'product_engine',
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'tradeshift-product-engine',
            'branch': 'dev-stable'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'tradeshift-product-engine',
        }
    },
    'business-analytics': {
        'hiera-name': 'business_analytics',
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'business-analytics',
            'branch': 'dev-stable-business-analytics'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'business-analytics',
        }
    },
    'business-analytics-etl': {
        'hiera-name': 'business_analytics_etl',
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'business-analytics',
            'branch': 'dev-stable-business-analytics-etl',
            'branch_suffix': '-etl'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'business-analytics',
        }
    },
    'business-analytics-etl-b': {
        'hiera-name': 'business_analytics_etl_b',
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'business-analytics',
            'branch': 'dev-stable-business-analytics-etl-b',
            'branch_suffix': '-etl-b'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'business-analytics',
        }
    },
    'Workflow': {
        'hiera-name': 'workflow',
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'Workflow',
            'branch': 'dev-stable'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'Workflow',
        }
    },
    'p2p-apps': {
        'hiera-name': 'p2p_apps',
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'p2p-apps',
            'branch': 'dev-stable'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'p2p-apps',
        }
    },
    'tradeshift-company-profile': {
        'hiera-name': 'company_profile',
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'tradeshift-company-profile',
            'branch': 'dev-stable'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'tradeshift-company-profile',
        }
    }
}

K8S_REPOS = {
    'orgs': {
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'orgs',
            'branch': 'dev-stable'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'orgs',
            'branch': 'master'
        }
    },
    'companies-onboarding': {
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'companies-onboarding',
            'branch': 'dev-stable'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'companies-onboarding',
            'branch': 'master'
        }
    },
    'tradeshift-clamav': {
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'tradeshift-clamav',
            'branch': 'dev-stable'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'tradeshift-clamav',
            'branch': 'master'
        }
    },
    'tradeshift-approval-service': {
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'tradeshift-approval-service',
            'branch': 'dev-stable'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'tradeshift-approval-service',
            'branch': 'master'
        }
    },
    'task-manager': {
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'task-manager',
            'branch': 'dev-stable'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'task-manager',
            'branch': 'master'
        }
    },
    'cloudscan-service': {
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'cloudscan-service',
            'branch': 'dev-stable'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'cloudscan-service',
            'branch': 'master'
        }
    }
}

IT_REPOS = {
    'Integration-Test': {
        'origin': {
            'org': 'TradeshiftCN',
            'repo_name': 'Integration-Test',
            'branch': 'dev-stable'
        },
        'upstream': {
            'org': 'Tradeshift',
            'repo_name': 'Integration-Test',
            'branch': 'master'
        }
    }
}
