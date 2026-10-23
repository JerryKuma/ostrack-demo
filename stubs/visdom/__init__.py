"""占位模块：OSTrack 在 `lib/vis/visdom_cus.py` 里 `import visdom`。

visdom 只用于 `--debug 1` 时的可视化，demo 里用不到。
真要可视化：`pip install visdom` 然后开 `visdom` 服务，再走官方 test.py --debug 1。
"""


class Visdom:
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        return lambda *args, **kwargs: None
