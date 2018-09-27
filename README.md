# code rebase toolkit for Tradeshift

## How to use code rebase toolkit
1. Make sure your directory structure looks like below example.
```
├── App-Service
├── Apps
├── Backend-Service
├── Frontend
├── Tradeshift-Proxy2
├── tradeshift-product-engine
├── tradeshift-company-profile
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

## How to create mutiple pull requests automatically

1. create pull request.
```bash
cd tradeshift-rebase-toolkit
python ./scripts/create_pr.py
```

