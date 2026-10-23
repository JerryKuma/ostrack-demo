# OSTrack on a 4 GB laptop: headless CPU demo

[中文说明](#中文说明) · [English](#english)

---

## 中文说明

> 在只有 **RTX 3050 Laptop（4 GB 显存）** 的笔记本上，把 [OSTrack](https://github.com/botaoye/OSTrack) 的**推理链路**跑通：
> 不开窗口、不装 CUDA、纯 CPU 出框。

![demo](results/demo.gif)

**这不是复现，是打通环境。** 没有 ground truth，就没有 PR/SR，也就没有「和论文差多少」这回事。评测和训练等服务器。

### 实测结果

| 项 | 值 |
|---|---|
| 模型 | OSTrack ViT-B，**384 输入**（search 384 / template 192） |
| 权重 | ModelScope `damo/cv_vitb_video-single-object-tracking_ostrack`，371,408,049 字节 |
| 设备 | CPU（torch 1.13.1+cpu） |
| 视频 | OpenCV 样例 `vtest.avi`，768×576，10 fps |
| 首帧初始化 | 8 ms |
| 30 帧 | 22.6 s → **1.33 FPS**（同一台机器另一次 17.1 s / 1.75 FPS） |
| 首帧框 | `[633, 240, 49, 85]` |
| 末帧框 | `[378, 178, 32, 87]` |

> 论文里的速度是单卡 RTX2080Ti 上的数字。**这里的 FPS 不能和论文比**，也不构成任何性能结论。

### 为什么需要这个仓库

官方代码有四个坑，任何一个都能让人卡半天：

1. **官方 demo 是交互式的**。`tracking/video_demo.py` 里 `cv2.namedWindow` + `imshow` + `waitKey`，没给框还要人手画。远程终端 / 无桌面环境直接卡死。
2. **`.cuda()` 写死**。`lib/test/tracker/ostrack.py` 里 `network.cuda()`、`hann2d(...).cuda()`，CPU 机器当场报错。
3. **权重在 Google Drive**。国内基本下不动，且 384/256 两个版本的权重**不能混用**（`pos_embed` 形状不同）。
4. **官方路径生成脚本在 Windows 上是坏的**。`create_default_local_file.py` 把路径拼进单引号字符串，`\u`、`\t` 被当成转义符，生成的文件甚至 import 不了。

这个仓库把四条都绕过去了，并且把踩过的坑写进了 [docs/pitfalls.md](docs/pitfalls.md)。

### 快速开始（Windows / CPU）

```powershell
git clone https://github.com/botaoye/OSTrack.git ..\OSTrack
git clone <this-repo> ostrack-demo
cd ostrack-demo

# 1. 建环境（Python 3.8）
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1

# 2. 修 local.py（官方脚本在 Windows 上会生成坏路径）
.\.venv\Scripts\python.exe scripts\make_local_config.py --ostrack ..\OSTrack

# 3. 下载权重（约 371 MB，走 ModelScope，国内直连）
.\.venv\Scripts\python.exe scripts\download_weights.py --ostrack ..\OSTrack

# 4. 样例视频（OpenCV 示例，约 8 MB）
.\.venv\Scripts\python.exe scripts\get_sample_video.py --out data\vtest.avi

# 5. 跑
.\.venv\Scripts\python.exe run_demo_cpu.py `
    --ostrack ..\OSTrack --video data\vtest.avi --box 638 236 50 86 `
    --out results\demo_30f.mp4 --max-frames 30 --metrics results\metrics.json
```

### 一个真实观察：跑到 60 帧，框会漂

第 30 帧之前目标一直跟得住；把 `--max-frames` 提到 60 之后，目标走进人群、又被灯柱挡了一下，框开始缩成一条贴在人边上。

这不是 bug，是这类单流跟踪器的典型失败模式：**没有模板更新机制，遮挡之后模板还是第一帧的那个**。也正好是「长时 / 遮挡 / 模板更新」这类工作的下手点。

### 引用

- 论文：Ye et al., *Joint Feature Learning and Relation Modeling for Tracking: A One-Stream Framework*, ECCV 2022. [arXiv:2203.11991](https://arxiv.org/abs/2203.11991)
- 代码：[botaoye/OSTrack](https://github.com/botaoye/OSTrack)（MIT）
- 权重：[ModelScope `damo/cv_vitb_video-single-object-tracking_ostrack`](https://www.modelscope.cn/models/damo/cv_vitb_video-single-object-tracking_ostrack)
- 样例视频：OpenCV `samples/data/vtest.avi`

### 许可

本仓库脚本 MIT，见 [LICENSE](LICENSE)。OSTrack 本身是 MIT（Copyright (c) 2022 Botao Ye），本仓库不包含其源码。样例视频版权归 OpenCV 所有。

---

## English

A minimal headless CPU runner for [OSTrack](https://github.com/botaoye/OSTrack) (ECCV 2022), tested on a 4 GB RTX 3050 Laptop.

It exists because the official demo requires an interactive cv2 window, hard-codes `.cuda()`, ships weights only on Google Drive, and its path-config generator produces broken `local.py` files on Windows.

**Scope:** environment bring-up only. No ground truth, no PR/SR, no benchmark numbers. 1.33 FPS on CPU is not comparable to the paper's RTX2080Ti figures.

```powershell
python run_demo_cpu.py --ostrack ..\OSTrack --video data\vtest.avi `
    --box 638 236 50 86 --out results\demo_30f.mp4 --max-frames 30
```
