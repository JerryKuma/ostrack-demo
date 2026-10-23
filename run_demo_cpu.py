"""Headless, CPU-only demo runner for OSTrack.

Why this file exists
--------------------
OSTrack's official `tracking/video_demo.py` opens a cv2 window, calls
`cv2.imshow` / `cv2.waitKey` and (with no box given) expects a human to draw a
box. That cannot run headless. It also hard-codes `.cuda()` in
`lib/test/tracker/ostrack.py`, so a CPU-only laptop cannot run it at all.

This runner:
  * takes the initial box from the command line,
  * reads frames with cv2 and writes a boxed .mp4,
  * monkey-patches `.cuda()` into a no-op when `--device cpu` (the default),
  * prints init time / FPS and can dump them to JSON.

Usage
-----
    python run_demo_cpu.py --ostrack /path/to/OSTrack \
        --video data/sample/vtest.avi --box 638 236 50 86 \
        --out results/demo.mp4 --max-frames 30

Tested with: Python 3.8, torch 1.13.1+cpu, timm 0.5.4, opencv-python-headless.
"""

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def parse_args():
    p = argparse.ArgumentParser(description='Headless OSTrack demo (CPU by default)')
    p.add_argument('--ostrack', default=os.environ.get('OSTRACK_ROOT', os.path.join(os.getcwd(), 'OSTrack')),
                   help='path to the OSTrack checkout')
    p.add_argument('--config', default='vitb_384_mae_ce_32x4_ep300',
                   help='experiments/ostrack/<config>.yaml without the extension')
    p.add_argument('--video', required=True, help='input video file')
    p.add_argument('--box', nargs=4, type=float, required=True, metavar=('X', 'Y', 'W', 'H'),
                   help='initial bounding box on the first frame')
    p.add_argument('--out', default='demo_out.mp4', help='output mp4 path')
    p.add_argument('--max-frames', type=int, default=30, help='0 = whole video')
    p.add_argument('--device', default='cpu', choices=['cpu', 'cuda'])
    p.add_argument('--metrics', default='', help='optional path to write a JSON summary')
    p.add_argument('--save-boxes', default='', help='optional path to write per-frame boxes as CSV')
    return p.parse_args()


def main():
    args = parse_args()

    ostrack = os.path.abspath(args.ostrack)
    if not os.path.isdir(ostrack):
        print('OSTrack checkout not found: %s' % ostrack)
        return 2

    # Local stubs must win over site-packages: OSTrack imports jpeg4py and
    # visdom at module level even though this demo never uses them.
    sys.path.insert(0, os.path.join(HERE, 'stubs'))
    sys.path.insert(0, ostrack)

    import torch
    if args.device == 'cpu':
        torch.Tensor.cuda = lambda self, *a, **k: self
        torch.nn.Module.cuda = lambda self, *a, **k: self

    import cv2
    from lib.test.evaluation import Tracker

    tracker_wrapper = Tracker('ostrack', args.config, 'video')
    params = tracker_wrapper.get_parameters()
    params.debug = 0
    params.tracker_name = 'ostrack'
    params.param_name = args.config
    tracker = tracker_wrapper.create_tracker(params)

    cap = cv2.VideoCapture(args.video)
    ok, frame = cap.read()
    if not ok:
        print('cannot read video: %s' % args.video)
        return 1

    src_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

    t0 = time.time()
    tracker.initialize(frame, {'init_bbox': list(args.box)})
    init_ms = (time.time() - t0) * 1000.0

    h, w = frame.shape[:2]
    writer = cv2.VideoWriter(args.out, cv2.VideoWriter_fourcc(*'mp4v'), src_fps, (w, h))
    boxes = []
    n = 0
    t1 = time.time()
    while True:
        if args.max_frames and n >= args.max_frames:
            break
        ok, frame = cap.read()
        if not ok:
            break
        out = tracker.track(frame)
        bb = [int(round(v)) for v in out['target_bbox']]
        boxes.append(bb)
        cv2.rectangle(frame, (bb[0], bb[1]), (bb[0] + bb[2], bb[1] + bb[3]), (0, 255, 0), 3)
        cv2.putText(frame, 'OSTrack  frame %d' % n, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        writer.write(frame)
        n += 1
    elapsed = time.time() - t1

    cap.release()
    writer.release()

    summary = {
        'config': args.config,
        'device': args.device,
        'video': os.path.basename(args.video),
        'init_box': list(args.box),
        'first_box': boxes[0] if boxes else None,
        'last_box': boxes[-1] if boxes else None,
        'frames': n,
        'init_ms': round(init_ms, 1),
        'elapsed_s': round(elapsed, 1),
        'fps': round(n / elapsed, 2) if elapsed else 0.0,
        'output': os.path.basename(args.out),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.metrics:
        with open(args.metrics, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
    if args.save_boxes:
        with open(args.save_boxes, 'w', encoding='utf-8', newline='\n') as f:
            f.write('frame,x,y,w,h\n')
            for i, bb in enumerate(boxes):
                f.write('%d,%d,%d,%d,%d\n' % (i, bb[0], bb[1], bb[2], bb[3]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
