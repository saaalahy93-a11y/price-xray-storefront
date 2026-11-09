#!/usr/bin/env python3
"""
Downloads only the required next batch of pre-rendered YouTube Shorts MP4s & Thumbnails
from the GitHub Release (`v1.0-shorts-vault`) inside GitHub Actions runners so the
repository stays lightweight while supporting 100% cloud-native autonomous uploads.
"""
import json
import os
import subprocess
import tarfile

BASE_DIR = os.environ.get(
    "PRICEXRAY_BASE_DIR",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)
UPLOADED_LOG = os.path.join(BASE_DIR, "uploaded_videos.json")
CALENDAR_PATH = os.path.join(BASE_DIR, "calendar_30days", "all_100_episodes.json")
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
RELEASE_TAG = os.environ.get("PRICEXRAY_RELEASE_TAG", "v1.0-shorts-vault")


def get_next_unuploaded_days(count=8):
    uploaded = {}
    if os.path.exists(UPLOADED_LOG):
        with open(UPLOADED_LOG, "r", encoding="utf-8") as f:
            uploaded = json.load(f)
    all_days = []
    if os.path.exists(CALENDAR_PATH):
        with open(CALENDAR_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            all_days = sorted(int(item["day"]) for item in data if "day" in item)
    else:
        all_days = list(range(1, 601))
    remaining = [d for d in all_days if str(d) not in uploaded]
    return remaining[:count]


def ensure_videos_downloaded(days):
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    missing_days = []
    for d in days:
        found = False
        for fmt in [f"Day_{d:02d}", f"Day_{d:03d}"]:
            cand = os.path.join(VIDEOS_DIR, f"{fmt}_PriceXRay_Short.mp4")
            if os.path.exists(cand) and os.path.getsize(cand) > 10000:
                found = True
                break
        if not found:
            missing_days.append(d)

    if not missing_days:
        print(f"✓ All target MP4s for days {days} are already present in {VIDEOS_DIR}.")
        return

    needed_archives = set()
    for d in missing_days:
        b_start = ((d - 1) // 50) * 50 + 1
        b_end = b_start + 49
        needed_archives.add(f"shorts_batch_{b_start:03d}_{b_end:03d}.tar")

    for archive in sorted(needed_archives):
        archive_path = os.path.join(BASE_DIR, archive)
        print(f"⬇ Downloading {archive} from GitHub Release {RELEASE_TAG}...")
        cmd = ["gh", "release", "download", RELEASE_TAG, "-p", archive, "-D", BASE_DIR, "--clobber"]
        res = subprocess.run(cmd, check=False)
        if res.returncode == 0 and os.path.exists(archive_path):
            print(f"📦 Extracting {archive} into {BASE_DIR}...")
            with tarfile.open(archive_path, "r") as tf:
                tf.extractall(path=BASE_DIR)
            os.remove(archive_path)
            print(f"✓ Extracted and cleaned up {archive}.")
        else:
            print(f"⚠ Could not download {archive} from release {RELEASE_TAG} (code {res.returncode}).")


if __name__ == "__main__":
    target_days = get_next_unuploaded_days(count=8)
    print(f"Target unuploaded days for this cloud run: {target_days}")
    if target_days:
        ensure_videos_downloaded(target_days)
