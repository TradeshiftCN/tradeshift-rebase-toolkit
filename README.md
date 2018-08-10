# code rebase toolkit for Tradeshift

## How to rebase
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

3. Install related dependency.
```bash
# install pip
brew install pip

# install shyaml
sudo pip install shyaml
``` 

4. Execute below commands to auto merge `Tradeshift/*/master` with `Tradeshift/*/dev-stable`.
```bash
cd tradeshift-rebase-toolkit
sh ./scripts/rebase.sh
```

5. Resolve all the conflicts, commit and push.

6. create pull request.
```bash
cd tradeshift-rebase-toolkit
python ./scripts/create_pr.py
```

## Something you have to know

1. Important! Resolve merge conflicts and execute `git commit` for every project(don't use `git commit -m xxx`)

2. Very important! you have to commit `apps` merge result with `git commit --no-verify`, otherwise a git hook would format all the code with `git commit`.

3. Very very important! Do not squash commits or use `squash and merge` from github. we need the commit logs.

## Something you may need to know

### Frontend
1. Check if `com.tradeshift:tradeshift-ubl` defined in `grails-app/conf/BuildConfig.groovy` is changed, since we have china specific change. If changed, rebase and release a new ubl jar package by the [jenkins job](https://cn.ci.bwtsi.cn/job/CB-Backend-Ubl-Manual-Release/)   
For example, in CN fork, our ubl version is `cn-83.7.13.1` and the code from Tradeshift is `83.7.18`. We need to check out this specific version of ubl and apply cn specific changes upon it and use the jenkins job to release `cn-83.7.18` version.

2. Find the chrome version defined in [tradeshift-puppet](https://github.com/Tradeshift/tradeshift-puppet/blob/testing/hiera/versions.yaml#L19) and run the [jenkins job](https://cn.ci.bwtsi.cn/job/tradeshift-chrome-release/) to release it to CDN.

### Apps
1. Check the base image in `docker/Dockerfile`, currently it should be tradeshift-docker-node:onbuild,
if the dockerfile in [tradeshift-docker-node](https://github.com/Tradeshift/tradeshift-docker-node/) repo is updated,
we need to rebase it with [this commit](https://github.com/TradeshiftCN/tradeshift-docker-node/commit/2a7cf11558e5c2d93e50c2b7b8ceaf758df99323),
and rebuild docker image by [jenkins job](https://cn.ci.bwtsi.cn/job/CB-Tradeshift-Docker-Node-Manual-Release/)

1. Don't try to resolve conflict in `package-lock.json`, just accept Tradeshift version and use below commands to regenerate a new one.
```bash
sed -i '' 's/npm.tradeshift.net/cn.npm.bwtsi.cn/g' package-lock.json
npm install
```

1. Inform everyone to use specific version of node defined in `.nvmrc` and npm defined in `jenkins.sh`.

### Backend-Service
1. Check `ubl.version` defined in `pom.xml`, follow Frontend step 1.

### Product-engine
1. Search all ImageStorageService bean, add `@Qualifier("qiniu")` annotation like below. 
```java
    @Autowired
    @Qualifier("qiniu")
    private final ImageStorageService imageStorageService;
```

## Reference

![Image of Relation](https://raw.githubusercontent.com/TradeshiftCN/tradeshift-rebase-toolkit/master/chart/Rebase%20relation.png)

