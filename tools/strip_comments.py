#!/usr/bin/env python3
"""
Strip comments from a set of files.

This script makes a .bak copy of each file before modifying it.
It removes:
- For JS/JSX files: block comments /* */ and single-line // comments
- For Python files: full-line comments starting with # (keeps inline comments)

Use carefully. Run from repo root:
  python3 tools/strip_comments.py
"""
import re
from pathlib import Path

TARGETS = [
    "src/backend/tests",
    "src/front/src",
    "src/front/e2e",
    "vite.config.js",
    "src/front/playwright.config.js",
]


def strip_js(content: str) -> str:
    # Remove block comments
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.S)

    # Remove single-line // comments but not inside strings
    # Simple approach: remove //... to line end when not in quotes
    def repl(match):
        s = match.group(0)
        # keep if '//' appears in string literals
        return re.sub(r"//.*", "", s)

    lines = []
    for line in content.splitlines():
        # remove // comments
        # but avoid removing in lines that contain 'http://' or 'https://'
        if "//" in line and "http://" not in line and "https://" not in line:
            # remove content after //
            parts = line.split("//")
            # if // appears inside quotes naive check: count quotes before //
            prefix = parts[0]
            # keep prefix (may remove trailing whitespace)
            line = prefix.rstrip()
        lines.append(line)
    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")


def strip_py(content: str) -> str:
    out = []
    for line in content.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            # drop full-line comment
            continue
        out.append(line)
    return "\n".join(out) + ("\n" if content.endswith("\n") else "")


def process_file(path: Path):
    text = path.read_text(encoding="utf-8")
    orig = text
    if path.suffix in (".js", ".jsx", ".ts", ".tsx"):
        new = strip_js(text)
    elif path.suffix == ".py":
        new = strip_py(text)
    else:
        # default: try js rules
        new = strip_js(text)

    if new != orig:
        bak = path.with_suffix(path.suffix + ".bak")
        bak.write_text(orig, encoding="utf-8")
        path.write_text(new, encoding="utf-8")
        print(f"Cleaned comments: {path}")


def gather_targets():
    files = []
    for t in TARGETS:
        p = Path(t)
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            for ext in ("*.py", "*.js", "*.jsx", "*.ts", "*.tsx"):
                files.extend(sorted(p.rglob(ext)))
        else:
            # try globs at repo root
            for ext in ("*.js", "*.jsx"):
                files.extend(sorted(Path(".").rglob(t)))
    # dedupe
    uniq = []
    seen = set()
    for f in files:
        if str(f) not in seen:
            uniq.append(f)
            seen.add(str(f))
    return uniq


def main():
    files = gather_targets()
    print(f"Found {len(files)} files to process.")
    for f in files:
        try:
            process_file(f)
        except Exception as e:
            print(f"Failed to process {f}: {e}")


if __name__ == "__main__":
    main()
