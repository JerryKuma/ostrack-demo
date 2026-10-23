# 建一个 Python 3.8 的 venv，装好跑 demo 需要的最小依赖。
# 用法： powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
#        （加 -Venv .venv-cpu 可以换目录）

param(
    [string]$Venv = ".venv"
)

$ErrorActionPreference = "Stop"

Write-Host "== 1/3 建 venv ($Venv) =="
py -3.8 -m venv $Venv
$vp = Join-Path $Venv "Scripts\python.exe"

Write-Host "== 2/3 升级 pip 并换清华源 =="
& $vp -m pip install -U "pip<25"
& $vp -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

Write-Host "== 3/3 装 torch(CPU) + 依赖 =="
# CPU 版 torch：几百 MB。CUDA 版 2 GB+，4 GB 显存的笔记本先不折腾。
& $vp -m pip install torch==1.13.1+cpu torchvision==0.14.1+cpu `
    --index-url https://download.pytorch.org/whl/cpu

# timm 必须是 0.5.x：0.9+ 把 timm.models.layers 的一部分接口挪走了
& $vp -m pip install timm==0.5.4 easydict pyyaml opencv-python-headless "numpy<1.24" matplotlib tensorboardX lmdb

Write-Host ""
Write-Host "done. python = $vp"
Write-Host "next: $vp scripts\make_local_config.py --ostrack ..\OSTrack"
