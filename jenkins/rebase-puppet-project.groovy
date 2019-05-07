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
        API_COMMIT = 'https://raw.githubusercontent.com/Tradeshift/tradeshift-puppet/production/hiera/versions.yaml'
    }
    parameters {
        string(name: 'COMPONENT_NAME', description: 'component name key in hiera versions.yaml')
        string(name: 'TARGET_BRANCH', defaultValue: 'rebase', description: 'Rebase target branch')
        string(name: 'CN_REPO', description: 'TradeshiftCN repository')
        string(name: 'CN_REFS', defaultValue: 'cn/dev-stable', description: 'git refs')
        string(name: 'TS_REPO', description: 'Tradeshift repository')
    }
    triggers {
        parameterizedCron('''
            H 1 * * * %COMPONENT_NAME=tradeshift_v4_apps;CN_REPO=Apps;TS_REPO=Apps
            H 1 * * * %COMPONENT_NAME=tradeshift_app_backend;CN_REPO=App-Service;TS_REPO=App-Backend
            H 1 * * * %COMPONENT_NAME=tradeshift_backend;CN_REPO=Backend-Service;TS_REPO=Backend-Service
            H 1 * * * %COMPONENT_NAME=business_analytics;CN_REPO=business-analytics;TS_REPO=business-analytics;TARGET_BRANCH=rebase-business-analytics;CN_REFS=cn/dev-stable-business-analytics
            H 1 * * * %COMPONENT_NAME=business_analytics_etl;CN_REPO=business-analytics;TS_REPO=business-analytics;TARGET_BRANCH=rebase-business-analytics-etl;CN_REFS=cn/dev-stable-business-analytics-etl
            H 1 * * * %COMPONENT_NAME=business_analytics_etl_b;CN_REPO=business-analytics;TS_REPO=business-analytics;TARGET_BRANCH=rebase-business-analytics-etl-b;CN_REFS=cn/dev-stable-business-analytics-etl-b
            H 1 * * * %COMPONENT_NAME=frontend;CN_REPO=Frontend;TS_REPO=Frontend
            H 1 * * * %COMPONENT_NAME=p2p_apps;CN_REPO=p2p-apps;TS_REPO=p2p-apps
            H 1 * * * %COMPONENT_NAME=company_profile;CN_REPO=tradeshift-company-profile;TS_REPO=tradeshift-company-profile
            H 1 * * * %COMPONENT_NAME=product_engine;CN_REPO=tradeshift-product-engine;TS_REPO=tradeshift-product-engine
            H 1 * * * %COMPONENT_NAME=tradeshift_proxy;CN_REPO=Tradeshift-Proxy2;TS_REPO=Tradeshift-Proxy2
            H 1 * * * %COMPONENT_NAME=workflow;CN_REPO=Workflow;TS_REPO=Workflow
            ''')
    }
    stages {
        stage ('Fetch') {
            steps {
                cleanWs()
                script {
                    VERSION = sh (returnStdout: true, script:"""
                    curl -H \"\${HEADER_AUTH}\" -O -L \"\${API_URL}\"
                    version=`cat versions.yaml | grep tradeshift::components::${COMPONENT_NAME}::version | sed -r \"s/^(tradeshift::components::${COMPONENT_NAME}::version: .*\')(.*)\'\$/\\2/\"`
                    if [ \${#version} -eq 40 ];then
                        echo \$version
                        exit
                    fi   
                      
                    commit=`curl -H \"\${HEADER_AUTH}\" -s -L \"https://api.github.com/repos/Tradeshift/${TS_REPO}/git/refs/tags/\$version\" | jq .object.sha | sed 's/\\\\"//g'`
                    if [ \${#commit} -eq 40 ];then
                        echo \$commit
                        exit
                    fi
                    
                    commit=`curl -H \"\${HEADER_AUTH}\" -s -L \"https://api.github.com/repos/Tradeshift/${TS_REPO}/git/refs/tags/v\$version\" | jq .object.sha | sed 's/\\\\"//g'`
                    if [ \${#commit} -eq 40 ]; then
                        echo \$commit
                    else
                        exit 1
                    fi
                    """)
                }
                sh "echo $VERSION"
            }
        }
        stage ('Rebase') {
            steps {
                build job: 'rebase-project', parameters: [
                        [$class: 'StringParameterValue', name: 'TARGET_BRANCH', value: "${TARGET_BRANCH}"],
                        [$class: 'StringParameterValue', name: 'CN_REPO', value: "${CN_REPO}"],
                        [$class: 'StringParameterValue', name: 'CN_REFS', value: "${CN_REFS}"],
                        [$class: 'StringParameterValue', name: 'TS_REPO', value: "${TS_REPO}"],
                        [$class: 'StringParameterValue', name: 'TS_REFS', value: "${VERSION}"]]
            }
        }
    }
}
