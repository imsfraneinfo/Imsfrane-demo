"""Remove the decorative north-east arrow from generated site assets."""
import re
import sys
from pathlib import Path

ARROW = re.compile(r'[ \t\u00a0]*(?:↗\ufe0f?|&#(?:8599|x2197);|&nearr;|&nearrow;|\\u2197|\\2197(?:[ \t])?)', re.I)

root = Path(sys.argv[1])
assert root.is_dir(), root
changed = 0
for path in root.rglob('*'):
    if not path.is_file() or path.suffix not in {'.html', '.css', '.js', '.json', '.svg'}:
        continue
    original = path.read_text(encoding='utf-8')
    updated = ARROW.sub('', original)
    if updated != original:
        path.write_text(updated, encoding='utf-8')
        changed += 1
print(f'Removed decorative diagonal arrows from {changed} files.')
