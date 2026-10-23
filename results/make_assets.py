"""把 demo_30f.mp4 转成首帧/末帧 PNG + 一个可以在 GitHub README 里直接显示的 GIF。"""

import os

import cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.join(HERE, 'demo_30f.mp4')
OUT = HERE

cap = cv2.VideoCapture(VIDEO)
frames = []
while True:
    ok, f = cap.read()
    if not ok:
        break
    frames.append(f)
cap.release()
print('frames read:', len(frames))

# 首帧 / 末帧（原分辨率）
cv2.imwrite(os.path.join(OUT, 'frame_000.png'), frames[0])
cv2.imwrite(os.path.join(OUT, 'frame_%03d.png' % (len(frames) - 1)), frames[-1])

# GIF：缩到 480 宽，10 fps
w = 480
h = int(frames[0].shape[0] * w / frames[0].shape[1])
imgs = []
for f in frames:
    rgb = cv2.cvtColor(cv2.resize(f, (w, h), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
    imgs.append(Image.fromarray(rgb))
gif_path = os.path.join(OUT, 'demo.gif')
imgs[0].save(gif_path, save_all=True, append_images=imgs[1:], duration=100, loop=0, optimize=True)
print('gif bytes:', os.path.getsize(gif_path))
