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
```bash
# install pip
brew install pip

# install shyaml
sudo pip install shyaml
``` 

2. Execute below commands to auto rebase.
```bash
cd tradeshift-rebase-toolkit
sh ./scripts/rebase.sh
```

3. Resolve merge conflicts and execute `git commit` for every project(don't use `git commit -m xxx`)

## Key point

### Frontend
1. Check if `com.tradeshift:tradeshift-ubl` defined in `grails-app/conf/BuildConfig.groovy` is changed, since we have china specific change.
If changed, rebase and release a new ubl jar package by the [jenkins job](https://cn.ci.bwtsi.cn/job/CB-Backend-Ubl-Manual-Release/)

2. Check if `tradeshift.chrome.stableVersion` defined in `grails-app/conf/Config.groovy` is changed.
If changed, release this new chrome version to ali cdn by [jenkins job](https://cn.ci.bwtsi.cn/job/tradeshift-chrome-release/)

### Apps
1. Check if `tradeshift-ui` in `package.json` is updated.
If changed, first, release the version to ali cdn by the [jenkins job](https://cn.ci.bwtsi.cn/job/CB-Tradeshift-UI-Manual-Release/configure)
second, update puppet like this [pull request](https://github.com/TradeshiftCN/tradeshift-puppet/pull/680/files)

2. Check the base image in `docker/Dockerfile`, currently it should be tradeshift-docker-node:onbuild,
if the dockerfile in [tradeshift-docker-node](https://github.com/Tradeshift/tradeshift-docker-node/) repo is updated,
we need to rebase it with [this commit](https://github.com/TradeshiftCN/tradeshift-docker-node/commit/2a7cf11558e5c2d93e50c2b7b8ceaf758df99323),
and rebuild docker image by [jenkins job](https://cn.ci.bwtsi.cn/job/CB-Tradeshift-Docker-Node-Manual-Release/)

3. Don't try to resolve conflict in `package-lock.json`, just accept Tradeshift version and use below commands to regenerate a new one.
```bash
sed -i '' 's/npm.tradeshift.net/cn.npm.bwtsi.cn/g' package-lock.json
npm install
```

4. Inform everyone to use specific version of node defined in `.nvmrc` and npm defined in `jenkins.sh`.

### Backend-Service
1. Check `ubl.version` defined in `pom.xml`, follow Frontend step 1.

### Product-engine
1. Search all ImageStorageService bean, add `@Qualifier("qiniu")` annotation like below. 
```java
    @Autowired
    @Qualifier("qiniu")
    private final ImageStorageService imageStorageService;
```

## create rebase pull request

## Rebase Relation

![Image of Relation](https://raw.githubusercontent.com/TradeshiftCN/tradeshift-rebase-toolkit/master/chart/Rebase%20relation.png)

