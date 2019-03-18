# code rebase toolkit for Tradeshift

# 运行

## 安装Miniconda

下载 [Miniconda](https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda-latest-MacOSX-x86_64.sh)

```bash
cd 下载 miniconda 的目录
bash Miniconda-latest-MacOSX-x86_64.sh
cd 到当前目录
conda env create -f env.yaml
conda activate rebase-toolkit
```

修改scripts/config.py

运行
```bash
python pileline.py
```
