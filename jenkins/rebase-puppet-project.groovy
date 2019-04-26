/*
1. fetch component version <br>
2. trigger rebase project <br>
*/
pipeline {
    agent any
    options {
        ansiColor('xterm')
        timestamps()
        timeout(time: 10, unit: 'MINUTES')
        disableConcurrentBuilds()
    }
    environment {
        GITHUB_TOKEN = credentials 'github_token'
        HEADER_AUTH = "Authorization: token ${GITHUB_TOKEN}"
        API_URL = 'https://raw.githubusercontent.com/Tradeshift/tradeshift-puppet/production/hiera/versions.yaml'
    }
    parameters {
        string(name: 'COMPONENT_NAME', description: 'component name key in hiera versions.yaml')
        string(name: 'CN_REPO', description: 'TradeshiftCN repository')
        string(name: 'TS_REPO', description: 'Tradeshift repository')
    }
    triggers {
        parameterizedCron('''
            H 0 * * * %COMPONENT_NAME=p2p_apps;CN_REPO=p2p-apps;TS_REPO=p2p-apps
            ''')
    }
    stages {
        stage ('Fetch') {
            steps {
                cleanWs()
                script {
                    VERSION = sh (returnStdout: true, script:"""
                    curl -H \"\${HEADER_AUTH}\" -O -L \"\${API_URL}\"
                    cat versions.yaml | grep ${COMPONENT_NAME} | sed -r \"s/^(tradeshift::components::.*::version: .*\')(.*)\'\$/\\2/\"
                    """)
                }
            }
        }
        stage ('Rebase') {
            steps {
                build job: 'rebase-project', parameters: [
                        [$class: 'StringParameterValue', name: 'CN_REPO', value: "${CN_REPO}"],
                        [$class: 'StringParameterValue', name: 'TS_REPO', value: "${TS_REPO}"],
                        [$class: 'StringParameterValue', name: 'TS_REFS', value: "${VERSION}"]]
            }
        }
    }
}
