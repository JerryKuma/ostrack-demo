# 环境问题与处理记录

按「现象 → 原因 → 处理」记录。环境为 Windows + Python 3.8.6 + torch 1.13.1+cpu，时间 2026-10-23。

## 1. 官方 demo 依赖窗口交互

**现象**：运行 `tracking/video_demo.py` 后进程停住，或在无桌面环境下报 `cv2.error`。

**原因**：`lib/test/evaluation/tracker.py` 在读取首帧后调用 `cv.VideoCapture` / `cv.namedWindow` / `cv.imshow`；未提供 `--optional_box` 时还会进入 `cv.selectROI`，等待人工绘制初始框。

**处理**：使用 `run_demo_cpu.py`，从命令行接收初始框，直接读取帧、绘制矩形并写出 mp4，不调用 cv2 窗口函数。

## 2. 跟踪器中直接调用 `.cuda()`

**现象**：`RuntimeError: No CUDA GPUs are available` 或 `Torch not compiled with CUDA enabled`。

**原因**：`lib/test/tracker/ostrack.py` 中 `network = network.cuda()` 与 `hann2d(...).cuda()` 为硬编码。

**处理**：在导入跟踪器前将 `Tensor.cuda`、`Module.cuda` 替换为空操作：

```python
import torch
torch.Tensor.cuda = lambda self, *a, **k: self
torch.nn.Module.cuda = lambda self, *a, **k: self
```

在 GPU 环境运行时应改为在源码中统一使用 `.to(device)`。

## 3. jpeg4py 未安装导致导入失败

**现象**：`ModuleNotFoundError: No module named 'jpeg4py'`；Windows 下 `pip install jpeg4py` 编译失败。

**原因**：`lib/train/data/image_loader.py` 在模块导入阶段即 `import jpeg4py`，与本次是否使用 jpg 序列无关。

**处理**：`stubs/jpeg4py.py` 提供占位模块。若需读取 LaSOT / LasHeR 的图像序列，改用 `opencv_loader`。

## 4. 未参与推理的依赖同样会阻断导入

**现象**：`ModuleNotFoundError: No module named 'visdom'` 或 `'tensorboardX'`。

**原因**：`lib/vis/visdom_cus.py`、`lib/train/admin/tensorboard.py` 位于导入链上，即使 `debug=0` 也会执行。

**处理**：`stubs/visdom/` 提供占位包（`visdom_cus.py` 同时导入 `visdom.server`，因此占位需为包）；`tensorboardX` 与 `matplotlib` 体积较小，直接安装。

## 5. `create_default_local_file.py` 生成的路径在 Windows 下无效

**现象**：`RuntimeError: YOU HAVE NOT SETUP YOUR local.py!!!`，或 `local.py` 导入时出现 `SyntaxError: (unicode error) 'unicodeescape'`。

**原因**：生成脚本将路径写入单引号字符串：

```python
settings.uav_path = 'D:\code\OSTrack\data\uav'
```

`\u` 被解析为 Unicode 转义，`\t`（如 `output\test`）被解析为制表符。

**处理**：`scripts/make_local_config.py` 用 raw string 重新生成 `lib/test/evaluation/local.py`，不使用官方生成器。

## 6. 权重版本与配置不匹配

**现象**：`RuntimeError: Error(s) in loading state_dict for OSTrack: size mismatch for backbone.pos_embed_z`。

**原因**：两个版本的输入分辨率不同：

| 配置 | template | search | `pos_embed_z` | `pos_embed_x` |
|---|---|---|---|---|
| `vitb_256_mae_ce_32x4_ep300` | 128 | 256 | 64 | 256 |
| `vitb_384_mae_ce_32x4_ep300` | 192 | 384 | 144 | 576 |

ModelScope 提供的 `pytorch_model.bin` 对应 384 版本。

**处理**：权重存放于 `output/checkpoints/train/ostrack/<config>/OSTrack_ep0300.pth.tar`，`--config` 与权重版本保持一致。

## 7. Python 3.8 自带 pip 无法安装部分依赖

**现象**：`ERROR: Internal Error.`，或依赖解析长时间无响应。

**原因**：Python 3.8.6 自带的 pip 20.2.1 版本过旧。

**处理**：先升级 `pip install -U "pip<25"`，再将索引切换至镜像源：

```powershell
python -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

`torch` 的 CPU wheel 位于 `download.pytorch.org`；PyPI 默认包为 CUDA 版本，体积超过 2 GB。

## 8. 权重文件格式

**现象**：`KeyError: 'net'`。

**原因**：官方代码使用 `torch.load(...)['net']`，要求文件为 `{'net': state_dict, ...}` 结构。ModelScope 提供的是完整 checkpoint，仅含 `net` 字段；若换成裸 state_dict 需自行封装。

**检查方式**：

```python
import torch
ck = torch.load('pytorch_model.bin', map_location='cpu')
print(list(ck.keys()))  # ['net']
```
