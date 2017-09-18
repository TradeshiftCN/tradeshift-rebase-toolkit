#!/bin/bash -e

cd ../tradeshift-puppet

# repos need to be sync
repos=( "Apps:tradeshift_v4_apps_server"
        "Apps-Server:apps_server"
        "App-Service:tradeshift_app_backend"
        "Backend-Service:tradeshift_backend"
        "tradeshift-company-profile:company_profile"
        "Frontend:frontend"
        "tradeshift-product-engine:product_engine"
        "Tradeshift-Proxy2:tradeshift_proxy"
        "Workflow:workflow"
        "p2p-apps:p2p_apps")

create_upstream() {
    if ! git remote | grep upstream >> /dev/null
    then
        echo "[$1] Git adding upstream."
        git remote add upstream git@github.com:Tradeshift/$1.git
    fi
}

do_sync() {
    repo=$1
    version=`cat hiera/versions.yaml | shyaml get-value tradeshift::components::tradeshift_v4_apps_server::version`
}

# fetch latest puppet
create_upstream tradeshift-puppet
git checkout upstream/production


# sync upstream
for i in "${repos[@]}"
do
    :
    KEY="${i%%:*}"
    VALUE="${i##*:}"
    echo "[$KEY] Syncing..."

    # goto working directory
    if [ ! -e "../$KEY" ]
    then
        echo "[$KEY] Directory missing!"
        echo "exiting..."
        exit 1;
    else
        cd ../${KEY}
    fi

    # create_upstream
    create_upstream ${KEY}

    # fetch codes from upstream
    echo "[$KEY] Git upstream fetching..."
    git fetch upstream
    git fetch upstream --prune --tags
    git tag | xargs git push origin

    echo "[$KEY] Git fetch successful."

    # checkout to production commit
    version=`cat ../tradeshift-puppet/hiera/versions.yaml | shyaml get-value tradeshift::components::${VALUE}::version`
    type=`cat ../tradeshift-puppet/hiera/versions.yaml | shyaml get-type tradeshift::components::${VALUE}::version`

    echo "[$KEY] Git checking to $version..."

    git checkout upstream/master
    git branch -D ts-master || true

    git checkout -b ts-master

    if [ ${#version} = 40 ]
    then
        git reset --hard ${version}
    else
        git reset --hard v${version} || git reset --hard ${version}
    fi

    git push -u

    echo "[$KEY] Git branch ts-master sync success."
done
