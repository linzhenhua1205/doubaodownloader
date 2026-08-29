"""Convert CRLF -> LF in text files under the newwiki2 docs folder.

Also strips UTF-8 BOM if present. Idempotent: if files are already LF, no change.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DISCOVER_NEWWIKI2_DOCS

DOCS = DISCOVER_NEWWIKI2_DOCS

# File extensions to normalize
TEXT_EXTS = {".md", ".json", ".py", ".sh", ".yml", ".yaml", ".txt", ".gitattributes"}


def long_path(p):
    abs_p = os.path.abspath(str(p))
    if abs_p.startswith("\\\\?\\"):
        return abs_p
    return "\\\\?\\" + abs_p


def normalize_file(path: Path):
    """Read raw bytes; strip BOM; convert CRLF to LF; write back. Return change info."""
    try:
        with open(long_path(path), "rb") as f:
            data = f.read()
    except Exception as e:
        return ("error", str(e))

    original_len = len(data)

    # Strip UTF-8 BOM
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]

    # Convert CRLF -> LF
    new_data = data.replace(b"\r\n", b"\n")

    # Also handle lone CR (old Mac style) -> LF, but only if no CRLF originally
    # (to avoid double-converting). Since we already converted CRLF to LF,
    # any remaining CR is a lone CR.
    new_data = new_data.replace(b"\r", b"\n")

    changed = (len(new_data) != original_len) or (new_data != data)

    if changed:
        try:
            with open(long_path(path), "wb") as f:
                f.write(new_data)
            return ("converted", None)
        except Exception as e:
            return ("write_error", str(e))
    return ("unchanged", None)


def main():
    total = 0
    converted = 0
    errors = 0
    by_ext = {}

    for fp in DOCS.rglob("*"):
        if not fp.is_file():
            continue
        if fp.suffix.lower() not in TEXT_EXTS:
            continue
        total += 1
        status, err = normalize_file(fp)
        by_ext[fp.suffix.lower()] = by_ext.get(fp.suffix.lower(), 0)
        if status == "converted":
            converted += 1
            by_ext[fp.suffix.lower()] += 1
        elif status == "error" or status == "write_error":
            errors += 1
            print(f"  ERR {fp}: {err}")

    print(f"Scanned: {total}")
    print(f"Converted (CRLF->LF / BOM stripped): {converted}")
    print(f"Errors: {errors}")
    print("By extension:")
    for ext, n in sorted(by_ext.items()):
        print(f"  {ext or '(none)'}: {n}")

    print("DONE")


if __name__ == "__main__":
    main()
