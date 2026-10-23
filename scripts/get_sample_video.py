"""下载 OpenCV 的样例视频 vtest.avi（广场行人，768x576，795 帧）。

用它是因为：有多个行人、有遮挡、有灯柱，正好能看出跟踪器的失败模式；
而且它是 OpenCV 官方 samples/data 里的公开样例，不涉及任何数据集授权。
"""

import argparse
import os
import urllib.request

URLS = [
    'https://raw.githubusercontent.com/opencv/opencv/master/samples/data/vtest.avi',
    'https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/vtest.avi',
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', default=os.path.join('data', 'vtest.avi'))
    args = p.parse_args()

    if os.path.exists(args.out):
        print('already there: %s (%d bytes)' % (args.out, os.path.getsize(args.out)))
        return 0

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    last = None
    for url in URLS:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=60) as r, open(args.out, 'wb') as f:
                f.write(r.read())
            print('saved %s (%d bytes) from %s' % (args.out, os.path.getsize(args.out), url))
            return 0
        except Exception as e:  # noqa: BLE001 - 换一个镜像再试
            last = e
            print('failed: %s (%s)' % (url, e))
    print('all mirrors failed:', last)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
