# Code rebase toolkit for Tradeshift China

# 依赖

## 安装 Miniconda
下载 [Miniconda](https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda-latest-MacOSX-x86_64.sh)。
```bash
cd 下载 miniconda 的目录
bash Miniconda-latest-MacOSX-x86_64.sh
cd 到当前目录
conda env create -f env.yaml
conda activate rebase-toolkit
```

## 或原生 Python 3
需要安装以下依赖：
```bash
pip3 install pyyaml coloredlogs tqdm GitPython
```

# 运行
```bash
cd scripts
cp config-template.py config.py # 首次运行时需要
```
修改 `config.py`，将其中的 `'change this'` 全部替换为合适的值。
```bash
python3 pipeline.py
```
