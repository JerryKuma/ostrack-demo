"""生成 lib/test/evaluation/local.py（Windows 安全版）。

官方 tracking/create_default_local_file.py 会把路径拼进单引号字符串，
在 Windows 上 `\\u`、`\\t` 会被当作转义符，生成的文件甚至 import 不了。
这里统一用 raw string 重写。

用法：
    python scripts/make_local_config.py --ostrack ..\\OSTrack
"""

import argparse
import os

TEMPLATE = '''from lib.test.evaluation.environment import EnvSettings


def local_env_settings():
    settings = EnvSettings()

    root = r'{root}'
    settings.prj_dir = root
    settings.save_dir = root + r'\\output'
    settings.network_path = root + r'\\output\\test\\networks'
    settings.results_path = root + r'\\output\\test\\tracking_results'
    settings.result_plot_path = root + r'\\output\\test\\result_plots'
    settings.segmentation_path = root + r'\\output\\test\\segmentation_results'

    settings.got10k_path = root + r'\\data\\got10k'
    settings.got10k_lmdb_path = root + r'\\data\\got10k_lmdb'
    settings.lasot_path = root + r'\\data\\lasot'
    settings.lasot_lmdb_path = root + r'\\data\\lasot_lmdb'
    settings.lasot_extension_subset_path_path = root + r'\\data\\lasot_extension_subset'
    settings.trackingnet_path = root + r'\\data\\trackingnet'
    settings.tnl2k_path = root + r'\\data\\tnl2k'
    settings.otb_path = root + r'\\data\\otb'
    settings.uav_path = root + r'\\data\\uav'
    settings.nfs_path = root + r'\\data\\nfs'
    settings.tc128_path = root + r'\\data\\TC128'
    settings.vot_path = root + r'\\data\\VOT2019'
    settings.vot18_path = root + r'\\data\\vot2018'
    settings.vot22_path = root + r'\\data\\vot2022'
    settings.itb_path = root + r'\\data\\itb'

    return settings
'''


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--ostrack', required=True, help='path to the OSTrack checkout')
    args = p.parse_args()

    root = os.path.abspath(args.ostrack).rstrip('\\/')
    dst = os.path.join(root, 'lib', 'test', 'evaluation', 'local.py')
    if not os.path.isdir(os.path.dirname(dst)):
        print('not an OSTrack checkout:', root)
        return 2

    with open(dst, 'w', encoding='utf-8', newline='\n') as f:
        f.write(TEMPLATE.format(root=root))
    print('wrote', dst)

    # 顺手把 checkpoint 目录建出来，省得下载脚本自己 mkdir
    os.makedirs(os.path.join(root, 'output', 'checkpoints', 'train', 'ostrack'), exist_ok=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
