# 踩过的坑

按「症状 → 原因 → 解法」记。都是 2026-10-23 在 Windows 10 + Python 3.8.6 + torch 1.13.1+cpu 上实测的。

---

## 1. 官方 demo 开窗口，无人值守跑不了

**症状**：`python tracking/video_demo.py ostrack vitb_384_mae_ce_32x4_ep300 video.mp4` 卡住，或者报 `cv2.error: ... The function is not implemented`。

**原因**：`lib/test/evaluation/tracker.py:186-191` 里 `cv.VideoCapture` 之后直接 `cv.namedWindow` + `cv.imshow`；不给 `--optional_box` 还会进 `cv.selectROI` 等人画框。

**解法**：用本仓库的 `run_demo_cpu.py`：自己读帧、自己 `cv2.rectangle`、自己写 mp4，全程不碰 GUI。

---

## 2. `.cuda()` 写死，CPU 机器直接崩

**症状**：`RuntimeError: No CUDA GPUs are available` 或 `Torch not compiled with CUDA enabled`。

**原因**：`lib/test/tracker/ostrack.py:24` `network = network.cuda()`，`:32` `hann2d(...).cuda()`。

**解法**：在 `import lib.test...` 之前把 `.cuda()` 打成空操作：

```python
import torch
torch.Tensor.cuda = lambda self, *a, **k: self
torch.nn.Module.cuda = lambda self, *a, **k: self
```

真正上显卡时不要长期靠这个补丁，应该把源码改成 `.to(device)`。

---

## 3. jpeg4py 在 Windows 上装不上

**症状**：`ModuleNotFoundError: No module named 'jpeg4py'`，`pip install jpeg4py` 编译失败（找不到 libjpeg-turbo）。

**原因**：`lib/train/data/image_loader.py:1` 在 **import 阶段**就 `import jpeg4py`，哪怕这次跑的是视频、用的是 cv2 loader。

**解法**：放一个空壳 `stubs/jpeg4py.py` 顶住 import。真要读 LaSOT/LasHeR 的 jpg 序列，改用 `opencv_loader`。

---

## 4. visdom / tensorboardX / matplotlib 这些「根本没用到」的包也会挡路

**症状**：`ModuleNotFoundError: No module named 'visdom'` 或 `'tensorboardX'`。

**原因**：`lib/vis/visdom_cus.py`、`lib/train/admin/tensorboard.py` 在 import 链上，即使 `debug=0`。

**解法**：visdom 用 `stubs/visdom/` 占位（注意它还会 `import visdom.server`，所以占位得是个包）；tensorboardX 和 matplotlib 直接 pip 装，体积小。

---

## 5. 官方 `create_default_local_file.py` 在 Windows 上生成坏路径

**症状**：`RuntimeError: YOU HAVE NOT SETUP YOUR local.py!!!`，或者 `SyntaxError: (unicode error) 'unicodeescape'`。

**原因**：生成器把路径写进单引号字符串：

```python
settings.uav_path = 'D:\code\OSTrack\data\uav'
```

`\u` 是 Unicode 转义、`\t`（`output\test`）是制表符，路径直接烂掉。

**解法**：用 `scripts/make_local_config.py` 重新生成（全部 raw string）。不要用官方那个。

---

## 6. 权重：Google Drive 下不动，384 和 256 不能混用

**症状**：`RuntimeError: Error(s) in loading state_dict for OSTrack: size mismatch for backbone.pos_embed_z: copying a param with shape torch.Size([1, 144, 768]) ... current model is torch.Size([1, 64, 768])`。

**原因**：两个版本的输入分辨率不同：

| config | template | search | `pos_embed_z` | `pos_embed_x` |
|---|---|---|---|---|
| `vitb_256_mae_ce_32x4_ep300` | 128 | 256 | 64 | 256 |
| `vitb_384_mae_ce_32x4_ep300` | 192 | 384 | 144 | 576 |

ModelScope 那份 `pytorch_model.bin` 是 **384** 版。

**解法**：权重放 `output/checkpoints/train/ostrack/<config>/OSTrack_ep0300.pth.tar`，`--config` 必须和权重版本一致。`scripts/download_weights.py` 会放在正确位置。

---

## 7. py3.8 自带的 pip 20.2.1 装不动新包

**症状**：`ERROR: Internal Error.` 或者解析依赖时无限转圈。

**原因**：Python 3.8.6 自带的 pip 太老，处理现代 wheel 元数据会出问题。

**解法**：先 `python -m pip install -U "pip<25"`，再把 index 换成清华源：

```powershell
python -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

torch 的 CPU wheel 在 `download.pytorch.org`，不要用 PyPI 上的默认包（那是 CUDA 版，2 GB+）。

---

## 8. 权重文件里是完整 checkpoint，不是裸 state_dict

**症状**：`KeyError: 'net'`，或者 `AttributeError: 'dict' object has no attribute ...`。

**原因**：官方代码 `torch.load(...)['net']`，要求文件是 `{'net': state_dict, ...}`。ModelScope 那份恰好就是完整 checkpoint（只有一个 `net` 键），可以直接用；如果换成裸 state_dict 的权重，要自己包一层。

**检查方法**：

```python
import torch
ck = torch.load('pytorch_model.bin', map_location='cpu')
print(list(ck.keys()))  # ['net']
```
