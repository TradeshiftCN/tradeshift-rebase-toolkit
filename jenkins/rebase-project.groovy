/*
1. checkout rebase branch <br>
2. merge CN_REFS <br>
3. merge TS_REFS <br>
4. tag the commit with format YYYY-MM-DD <br>
5. push the branch and tag <br><br>

TODO <br>
1. run test and create PR. <br>
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
        SLACK_TOKEN = credentials 'SLACK_TOKEN'
        SLACK_SECRET_ID = credentials 'SLACK_SECRET_ID'
        SLACK_SECRET_TOKEN = credentials 'SLACK_SECRET_TOKEN'
    }
    parameters {
        string(name: 'CN_REPO', description: 'TradeshiftCN repository')
        string(name: 'CN_REFS', defaultValue: 'cn/dev-stable', description: 'git refs')
        string(name: 'TS_REPO', description: 'Tradeshift repository')
        string(name: 'TS_REFS', defaultValue: 'ts/master', description: 'git refs')
    }
    triggers {
        parameterizedCron('''
            H 0 * * * %CN_REPO=Integration-Test;TS_REPO=Integration-Test
            H 0 * * * %CN_REPO=companies-onboarding;TS_REPO=companies-onboarding
            H 0 * * * %CN_REPO=event-app-handler;TS_REPO=event-app-handler
            H 0 * * * %CN_REPO=orgs;TS_REPO=orgs
            ''')
    }
    stages {
        stage ('SCM'){
            steps {
                cleanWs()
                checkout([
                        $class: 'GitSCM',
                        extensions: [],
                        userRemoteConfigs: [[name: 'cn', url: "git@github.com:TradeshiftCN/${CN_REPO}.git"]]
                ])
                checkout([
                        $class: 'GitSCM',
                        extensions: [],
                        userRemoteConfigs: [[name:'ts', url: "git@github.com:Tradeshift/${TS_REPO}.git"]]
                ])
            }
        }
        stage('Merge') {
            steps {
                sh '''
                    export GIT_COMMITTER_EMAIL=jenkins.cn@tradeshift.com
                    export GIT_COMMITTER_NAME=cntsjenkins
                    export GIT_AUTHOR_NAME=cntsjenkins

                    set -e
                    git reset --hard
                    git checkout -B rebase cn/rebase || git checkout -B rebase ${CN_REFS}

                    git merge ${CN_REFS}
                    git merge ${TS_REFS}

                    tag=rebase-`date '+%Y-%m-%d'`

                    git tag -f ${tag}
                    git push cn HEAD:refs/heads/rebase
                    git push -f cn HEAD:refs/tags/${tag}
                '''
            }
        }
    }
    post {
        success {
            sh """
            SLACK_MSG='Build <${BUILD_URL}|${BUILD_DISPLAY_NAME}> `${CN_REPO}` ok. :sunflower:'
            SLACK_URL='https://hooks.slack.com/services/${SLACK_TOKEN}/${SLACK_SECRET_TOKEN}/${SLACK_SECRET_ID}'
            SLACK_PAYLOAD='payload={\"channel\": \"#cn-rebase\", \"username\": \"CICD\", \"text\": \"'\${SLACK_MSG}'\", \"icon_emoji\": \":tradeshift:\"}'
            curl -X POST --data-urlencode \"\${SLACK_PAYLOAD}\" \"\${SLACK_URL}\"
            """
        }
        failure {
            sh """
            SLACK_MSG='Build <${BUILD_URL}|${BUILD_DISPLAY_NAME}> `${CN_REPO}` fail! :upside_down_face:'
            SLACK_URL='https://hooks.slack.com/services/${SLACK_TOKEN}/${SLACK_SECRET_TOKEN}/${SLACK_SECRET_ID}'
            SLACK_PAYLOAD='payload={\"channel\": \"#cn-rebase\", \"username\": \"CICD\", \"text\": \"'\${SLACK_MSG}'\", \"icon_emoji\": \":tradeshift:\"}'
            curl -X POST --data-urlencode \"\${SLACK_PAYLOAD}\" \"\${SLACK_URL}\"
            """
        }
    }
}