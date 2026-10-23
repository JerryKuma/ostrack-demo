import os
import urllib.request

MODELSCOPE_URL = ('https://www.modelscope.cn/api/v1/models/'
                  'damo/cv_vitb_video-single-object-tracking_ostrack/repo'
                  '?Revision=master&FilePath=pytorch_model.bin')
EXPECTED_BYTES = 371408049  # listed on ModelScope; checked 2026-10-23


def download(url, dst):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    total = 0
    with urllib.request.urlopen(req, timeout=60) as r, open(dst, 'wb') as f:
        expected = int(r.headers.get('Content-Length') or 0)
        got = 0
        while True:
            chunk = r.read(1024 * 512)
            if not chunk:
                break
            f.write(chunk)
            got += len(chunk)
            if expected and got // (50 * 1024 * 1024) != total // (50 * 1024 * 1024):
                print('  %.0f / %.0f MB' % (got / 1e6, expected / 1e6), flush=True)
            total = got
    return total


def main():
    import argparse
    p = argparse.ArgumentParser(description='Download OSTrack ViT-B/384 weights from ModelScope')
    p.add_argument('--ostrack', required=True, help='path to the OSTrack checkout')
    p.add_argument('--config', default='vitb_384_mae_ce_32x4_ep300')
    args = p.parse_args()

    dst_dir = os.path.join(args.ostrack, 'output', 'checkpoints', 'train', 'ostrack', args.config)
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, 'OSTrack_ep0300.pth.tar')

    if os.path.exists(dst) and os.path.getsize(dst) == EXPECTED_BYTES:
        print('already there:', dst)
        return 0

    print('downloading from ModelScope ...')
    size = download(MODELSCOPE_URL, dst)
    print('saved %s (%d bytes)' % (dst, size))
    if size != EXPECTED_BYTES:
        print('WARNING: expected %d bytes, got %d — file may be truncated' % (EXPECTED_BYTES, size))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
