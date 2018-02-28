# code rebase toolkit for Tradeshift

## rebase
1. Make sure your directory structure looks like below example.
```
├── App-Service
├── Apps
├── Backend-Service
├── Frontend
├── Tradeshift-Proxy2
├── tradeshift-company-profile
├── tradeshift-product-engine
├── Workflow
├── p2p-apps
├── tradeshift-puppet
├── tradeshift-rebase-toolkit
```

2. Make sure all project has no uncommited changes.

2. Install related dependency.
```
# install pip
brew install pip

# install shyaml
pip install shyaml
``` 

2. Execute below commands to auto rebase.
```
cd tradeshift-rebase-toolkit
sh ./scripts/rebase.sh
```

3. Resolve merge conflicts and execute `git commit` for every project(don't use `git commit -m xxx`)

## Key point

### Frontend
1. Check if `com.tradeshift:tradeshift-ubl` defined in `grails-app/conf/BuildConfig.groovy` is changed, since we have china specific change.
If changed, rebase and release a new ubl jar package by the [jenkins job](http://jenkins.bwtsi.cn:8080/job/Backend-Ubl/)

2. Check if `tradeshift.chrome.stableVersion` defined in `grails-app/conf/Config.groovy` is changed.
If changed, release this new chrome version to ali cdn by jenkins job (TBD)

### Apps
1. Check if `tradeshift-ui` in `package.json` is updated.
If changed, first, release the version to ali cdn by the [jenkins job](http://t.jenkins.bwtsi.cn:8080/view/release/job/tradeshift-ui-release)
second, update puppet like this [pull request](https://github.com/TradeshiftCN/tradeshift-puppet/pull/680/files)

2. Check the base image in `docker/Dockerfile`, currently it should be tradeshift-docker-node:onbuild,
if the dockerfile in [tradeshift-docker-node](https://github.com/Tradeshift/tradeshift-docker-node/) repo is updated,
we need to rebase it with [this commit](https://github.com/TradeshiftCN/tradeshift-docker-node/commit/2a7cf11558e5c2d93e50c2b7b8ceaf758df99323),
and rebuild docker image by [jenkins job](http://t.jenkins.bwtsi.cn:8080/view/release/job/tradeshift-docker-node-release/)

3. Don't try to resolve conflict in `package-lock.json`, just accept Tradeshift version and use below commands to regenerate a new one.
```
cat package-lock.json | sed -e "s/npm.tradeshift.net/cn.npm.bwtsi.cn/g" | tee package-lock.json
npm install
```

4. Announce everyone to use node version defined in `.nvmrc` and npm version defined in `jenkins.sh`.

### Backend-Service
1. Check `ubl.version` defined in `pom.xml`, follow Frontend step 1.

## create rebase pull request

