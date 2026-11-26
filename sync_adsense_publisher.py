"""Align AdSense tags and ads.txt with the active publisher."""
from pathlib import Path
import re
import sys

PUBLISHER = "3106160668387388"
LOCALES = ("fr", "en", "ar", "es")
SCRIPT = re.compile(
    r"<script\b(?=[^>]*\bsrc\s*=\s*['\"][^'\"]*/adsbygoogle\.js)[^>]*>\s*</script>",
    re.IGNORECASE,
)
TAG = (
    '<script async src="https://pagead2.googlesyndication.com/pagead/js/'
    f'adsbygoogle.js?client=ca-pub-{PUBLISHER}" crossorigin="anonymous"></script>'
)


def sync(root):
    updated = 0
    home_pages = {root / lang / "index.html" for lang in LOCALES}
    for path in root.rglob("*.html"):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        original = path.read_text(encoding="utf-8")
        page = original.replace("ca-pub-5598024978912334", f"ca-pub-{PUBLISHER}")
        if (path in home_pages or SCRIPT.search(page)) and SCRIPT.findall(page) != [TAG]:
            page = SCRIPT.sub("", page)
            page, count = re.subn(r"[ \t]*(?:\n[ \t]*)?</head\s*>", "\n" + TAG + "\n</head>", page, count=1, flags=re.I)
            if count != 1:
                raise ValueError(f"Missing head: {path}")
        if page != original:
            path.write_text(page, encoding="utf-8")
            updated += 1

    for path in home_pages:
        assert path.read_text(encoding="utf-8").count(TAG) == 1, path

    ads = root / "ads.txt"
    lines = ads.read_text(encoding="utf-8").splitlines() if ads.exists() else []
    entry = f"google.com, pub-{PUBLISHER}, DIRECT, f08c47fec0942fa0"
    lines = [line for line in lines if line.strip() != entry and "pub-5598024978912334" not in line]
    ads.write_text("\n".join([*lines, entry]) + "\n", encoding="utf-8")
    print(f"Verified all four language homepages. Updated {updated} HTML files.")


if __name__ == "__main__":
    sync(Path(sys.argv[1]))
