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
        "p2p-apps:p2p_apps")

report=""

verify_directory_structure() {
    echo "${green}Verifying directory structure.${reset}"
    for i in "${repos[@]}"
    do
        :
        KEY="${i%%:*}"
        VALUE="${i##*:}"
        if [ ! -e "../$KEY" ]
        then
            echo "${red}[$KEY] Directory missing!${reset}"
            echo "${red}[$KEY] Exiting...${reset}"
            exit 1;
        fi
    done
    echo "${green}Verify directory structure successful.${reset}"
}

create_upstream() {
    if ! git remote | grep upstream >> /dev/null
    then
        echo "${green}[$1] Git adding upstream.${reset}"
        git remote add upstream git@github.com:Tradeshift/$1.git
    fi
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
create_upstream tradeshift-puppet
git checkout upstream/production


verify_directory_structure

# do rebase
{ for i in "${repos[@]}"
do
    :
    KEY="${i%%:*}"
    VALUE="${i##*:}"

    # goto working directory
    echo "${green}[$KEY] Rebasing...${reset}"
    cd ../${KEY}

    # create_upstream
    create_upstream ${KEY}

    # fetch from upstream
    echo "${green}[$KEY] Git upstream fetching...${reset}"
    fetch_upstream
    echo "${green}[$KEY] Git fetch successful.${reset}"

    # checkout based on puppet version
    version=`cat ../tradeshift-puppet/hiera/versions.yaml | shyaml get-value tradeshift::components::${VALUE}::version`
    type=`cat ../tradeshift-puppet/hiera/versions.yaml | shyaml get-type tradeshift::components::${VALUE}::version`

    if [ -n "`is_commit_or_tag_exsiting v${version}`" ]; then
        echo "${green}[$KEY]git checkout v${version}${reset}"
        git checkout v${version}
    elif [ -n "`is_commit_or_tag_exsiting ${version}`" ]; then
        echo "${green}[$KEY]git checkout ${version}${reset}"
        git checkout ${version}
    else
        echo "${red}[$KEY] Git commit ${version} missing!${reset}"
        echo "${red}[$KEY] Exiting...${reset}"
        exit 1
    fi

    # create rebase branch
    echo "${green}[$KEY] Create rebase branch rebase_$(date +%Y_%m_%d)...${reset}"
    if [ -n "`is_branch_exsiting rebase_$(date +%Y_%m_%d)`" ]; then
        git branch -D rebase_$(date +%Y_%m_%d)
    fi
    git co -b rebase_$(date +%Y_%m_%d)

    # merge rebase branch
    echo "${green}[$KEY] Merging origin/feature-valeo.${reset}"
    git fetch origin
    git merge origin/feature-valeo  --no-commit \
        && report="$report${green}[$KEY] Automatic merge went well; commit the result manually.${reset}\n" \
        || report="$report${red}[$KEY] Automatic merge failed; fix conflicts and then commit the result.${reset}\n"

done

echo ""
echo "${green}*************REBASE REPORT****************${reset}"
echo -e ${report}
echo "${green}Auto rebase finished, Please resolve all the conflict and commit manually.${reset}"
}
