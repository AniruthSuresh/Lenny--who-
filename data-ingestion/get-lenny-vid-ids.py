import subprocess
import os

PLAYLIST_URL = "https://www.youtube.com/playlist?list=PL2fLjt2dG0N6unOOF3nHWYGcJJIQR1NKm"
MAX_VIDEOS = 100

OUTPUT_DIR = "../data/raw/youtube"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "video_ids.txt")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_video_ids(playlist_url, max_videos):
    """
    Uses yt-dlp to reliably extract video IDs from a playlist.
    """
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--get-id",
        playlist_url,
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )

    video_ids = result.stdout.strip().split("\n")
    return video_ids[:max_videos]


if __name__ == "__main__":
    ids = get_video_ids(PLAYLIST_URL, MAX_VIDEOS)

    with open(OUTPUT_FILE, "w") as f:
        for vid in ids:
            f.write(f"{vid}\thttps://youtu.be/{vid}\n")

    print(f"[OK] Saved {len(ids)} video IDs to {OUTPUT_FILE}")
