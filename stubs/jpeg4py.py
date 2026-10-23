# 占位模块：OSTrack 的 `lib/train/data/image_loader.py` 在 import 阶段就会
# `import jpeg4py`，而 jpeg4py 在 Windows 上基本装不上（需要 libjpeg-turbo）。
# 这个 demo 全程用 cv2 读图，不会调到 jpeg4py，所以用这个空壳顶住 import。
#
# 真要在 Windows 上跑 LaSOT/LasHeR 的 jpg 序列：把 image_loader 换成
# `opencv_loader`，或者老老实实装 jpeg4py 的 Windows wheel。


class JPEG:
    def __init__(self, *args, **kwargs):
        raise RuntimeError(
            'jpeg4py stub: this demo does not need jpeg4py. '
            'Use opencv_loader if you need to read image folders.'
        )
