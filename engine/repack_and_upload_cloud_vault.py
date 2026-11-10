#!/usr/bin/env python3
"""
Repacks all 600 V2 Studio MP4s + Thumbnails into 12 cloud vault archives
(shorts_batch_001_050.tar .. shorts_batch_551_600.tar) and uploads them
with --clobber to GitHub Release `v1.0-shorts-vault` on `saaalahy93-a11y/price-xray-storefront`.
"""
import argparse
import os
import subprocess
import tarfile

BASE_DIR = "/Users/ahmedalsalahy/.gemini/antigravity/scratch/factory-twin-shorts"
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
PACKS_DIR = os.path.join(BASE_DIR, "upload_ready_30_days")
DEPLOY_REPO = os.path.join(BASE_DIR, "gh_pages_deploy")
RELEASE_TAG = "v1.0-shorts-vault"


def pack_and_upload_batch(b_start, b_end, upload=True):
    tar_name = f"shorts_batch_{b_start:03d}_{b_end:03d}.tar"
    tar_path = os.path.join("/tmp", tar_name)
    added = 0
    with tarfile.open(tar_path, "w") as tf:
        for d in range(b_start, b_end + 1):
            mp4_name = f"Day_{d:02d}_PriceXRay_Short.mp4"
            thumb_name = f"Day_{d:02d}_Thumbnail.png"
            mp4_path = os.path.join(VIDEOS_DIR, mp4_name)
            if not os.path.exists(mp4_path):
                mp4_path = os.path.join(PACKS_DIR, f"Day_{d:02d}", mp4_name)
            thumb_path = os.path.join(VIDEOS_DIR, thumb_name)
            if not os.path.exists(thumb_path):
                thumb_path = os.path.join(PACKS_DIR, f"Day_{d:02d}", thumb_name)

            if os.path.exists(mp4_path):
                tf.add(mp4_path, arcname=f"videos/{mp4_name}")
                added += 1
            if os.path.exists(thumb_path):
                tf.add(thumb_path, arcname=f"videos/{thumb_name}")

    sz_mb = os.path.getsize(tar_path) / (1024 * 1024)
    print(f"📦 Packed {tar_name} ({added} MP4s + thumbnails, {sz_mb:.1f} MB)")

    if upload:
        cmd = ["gh", "release", "upload", RELEASE_TAG, tar_path, "--clobber", "--repo", "saaalahy93-a11y/price-xray-storefront"]
        res = subprocess.run(cmd, check=False)
        if res.returncode == 0:
            print(f"☁️ Uploaded {tar_name} to GitHub Release {RELEASE_TAG}!")
        else:
            print(f"⚠ Upload returned {res.returncode} for {tar_name}")
    if os.path.exists(tar_path):
        os.remove(tar_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=str, default="all", help="e.g. '1-50' or 'all'")
    parser.add_argument("--no-upload", action="store_true")
    args = parser.parse_args()

    if args.batch == "all":
        batches = [(i, i + 49) for i in range(1, 601, 50)]
    else:
        s, e = args.batch.split("-", 1)
        batches = [(int(s), int(e))]

    for b_s, b_e in batches:
        pack_and_upload_batch(b_s, b_e, upload=(not args.no_upload))


if __name__ == "__main__":
    main()
