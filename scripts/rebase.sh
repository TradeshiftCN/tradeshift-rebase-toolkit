#!/bin/bash -e

cd ../tradeshift-puppet

red=`tput setaf 1`
green=`tput setaf 2`
reset=`tput sgr0`

# repos need to be rebase
repos=( "Apps:tradeshift_v4_apps"
        "App-Service:tradeshift_app_backend"
        "Backend-Service:tradeshift_backend"
        "tradeshift-company-profile:company_profile"
        "Frontend:frontend"
        "tradeshift-product-engine:product_engine"
        "Tradeshift-Proxy2:tradeshift_proxy"
        "Workflow:workflow"
        "p2p-apps:p2p_apps"
        "orgs:orgs_service")

report=""

verify_directory_structure() {
    echo "${green}Verifying directory structure.${reset}"
    for i in "${repos[@]}"
    do
        :
        COMPONENT="${i%%:*}"
        if [ ! -e "../$COMPONENT" ]
        then
            echo "${red}[$COMPONENT] Directory missing!${reset}"
            echo "${red}[$COMPONENT] Exiting...${reset}"
            exit 1;
        fi
    done
    echo "${green}Verify directory structure successful.${reset}"
}

reset_remote() {
    if git remote | grep $1 >> /dev/null
    then
        git remote remove $1
    fi
    git remote add $1 $2
}

reset_remote_upstream() {
    echo "${green}[$1] Git reseting upstream.${reset}"
    reset_remote upstream git@github.com:Tradeshift/$1.git
}

reset_remote_origin() {
    echo "${green}[$1] Git reseting origin.${reset}"
    reset_remote origin git@github.com:TradeshiftCN/$1.git
}

is_branch_exsiting() {
    echo "`git show-ref refs/heads/$1`"
}

is_commit_or_tag_exsiting() {
    if git cat-file -e $1 2> /dev/null
    then
      echo exists
    fi
}

fetch_upstream() {
    git fetch upstream
    git fetch upstream --prune --tags
    git tag | xargs git push origin
}

# fetch latest puppet
reset_remote_origin tradeshift-puppet
reset_remote_upstream tradeshift-puppet
echo "${green}[tradeshift-puppet] Fetching latest...${reset}"
git fetch upstream
git checkout upstream/production


verify_directory_structure

# do rebase
{ for i in "${repos[@]}"
do
    :
    COMPONENT="${i%%:*}"
    COMPONENT_NAME="${i##*:}"

    # goto working directory
    echo "${green}[$COMPONENT] Rebasing...${reset}"
    cd ../${COMPONENT}

    # reset_remote_upstream
    reset_remote_origin ${COMPONENT}
    reset_remote_upstream ${COMPONENT}

    # fetch from upstream
    echo "${green}[$COMPONENT] Git upstream fetching...${reset}"
    fetch_upstream
    echo "${green}[$COMPONENT] Git fetch successful.${reset}"

    # checkout based on puppet version
    version=`cat ../tradeshift-puppet/hiera/versions.yaml | shyaml get-value tradeshift::components::${COMPONENT_NAME}::version`
    type=`cat ../tradeshift-puppet/hiera/versions.yaml | shyaml get-type tradeshift::components::${COMPONENT_NAME}::version`

    if [ -n "`is_commit_or_tag_exsiting v${version}`" ]; then
        echo "${green}[$COMPONENT]git checkout v${version}${reset}"
        git checkout v${version}
    elif [ -n "`is_commit_or_tag_exsiting ${version}`" ]; then
        echo "${green}[$COMPONENT]git checkout ${version}${reset}"
        git checkout ${version}
    else
        echo "${red}[$COMPONENT] Git commit ${version} missing!${reset}"
        echo "${red}[$COMPONENT] Exiting...${reset}"
        exit 1
    fi

    # create rebase branch
    echo "${green}[$COMPONENT] Create rebase branch rebase-$(date +%Y-%m-%d)...${reset}"
    if [ -n "`is_branch_exsiting rebase-$(date +%Y-%m-%d)`" ]; then
        git branch -D rebase-$(date +%Y-%m-%d)
    fi
    git co -b rebase-$(date +%Y-%m-%d)

    # merge rebase branch
    echo "${green}[$COMPONENT] Merging origin/dev-stable.${reset}"
    git fetch origin
    git merge origin/dev-stable --no-commit \
        && report="$report${green}[$COMPONENT] Automatic merge went well; commit the result manually.${reset}\n" \
        || report="$report${red}[$COMPONENT] Automatic merge failed; fix conflicts and then commit the result.${reset}\n"

done

echo ""
echo "${green}*************REBASE REPORT****************${reset}"
echo -e ${report}
echo "${green}Auto rebase finished, Please resolve all the conflict and commit manually.${reset}"
}
