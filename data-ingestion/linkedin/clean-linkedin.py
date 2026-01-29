import os
import json
import re
import unicodedata
from tqdm import tqdm

import re
# --------------------
# Paths
# --------------------
RAW_DIR = "../../data/raw/linkedin/"
CLEAN_DIR = "../../data/processed/linkedin"

os.makedirs(CLEAN_DIR, exist_ok=True)


def normalize_unicode(text: str) -> str:
    """
    Json renders " " as special unicode spaces -> so remove thosee
    Normalize smart quotes, apostrophes, dashes, ellipses, etc.
    """
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)

    replacements = {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "—": "-",
        "–": "-",
        "…": "...",
    }

    for src, tgt in replacements.items():
        text = text.replace(src, tgt)

    return text


def normalize_whitespace(text: str) -> str:
    """
    - Collapse all newlines to spaces
    - Collapse multiple spaces/tabs into a single space
    - Strip leading/trailing spaces
    """
    if not text:
        return ""

    text = re.sub(r'\s+', ' ', text)  # Collapse all whitespace (spaces, tabs, newlines) into single space
    return text.strip()



def strip_tracking_params(url: str) -> str:
    """
    Remove LinkedIn tracking params like utm_source, rcm, etc.
    """
    if not url:
        return ""

    return url.split("?")[0]


def soften_ctas(text: str) -> str:
    """
    Remove aggressive CTA spam but keep intent.
    """
    patterns = [
        r"→\s*Subscribe.*",
        r"→\s*Listen now.*",
        r"Listen now\s*👇.*",
    ]

    for p in patterns:
        text = re.sub(p, "", text, flags=re.IGNORECASE)

    return text.strip()


def clean_linkedin_text(text: str) -> str:
    text = normalize_unicode(text)
    text = normalize_whitespace(text)
    text = soften_ctas(text)
    return text


# --------------------
# Main processing
# --------------------
def main():
    files = [f for f in os.listdir(RAW_DIR) if f.endswith(".json")]
    print(f"[INFO] Found {len(files)} LinkedIn posts")

    for filename in tqdm(files, desc="Cleaning LinkedIn posts"):
        in_path = os.path.join(RAW_DIR, filename)
        out_path = os.path.join(CLEAN_DIR, filename)

        # Idempotent
        if os.path.exists(out_path):
            continue

        with open(in_path, "r") as f:
            data = json.load(f)

        cleaned = {
            "source": "linkedin",
            "post_id": data.get("post_id"),
            "url": strip_tracking_params(data.get("url")),
            "author": data.get("author", "Lenny Rachitsky"),
            "posted_at": data.get("posted_at"),
            "likes": data.get("likes", 0),
            "text": clean_linkedin_text(data.get("text", "")),
        }

        with open(out_path, "w") as f:
            json.dump(cleaned, f, indent=2, ensure_ascii=False)

    print(f"[OK] Clean LinkedIn data written to {CLEAN_DIR}")


if __name__ == "__main__":
    main()
