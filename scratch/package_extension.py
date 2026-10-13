import os
import zipfile
from pathlib import Path

EXTENSION_DIR = Path(r"c:\Docs\Phishing_Detection\extension")
OUTPUT_ZIP = Path(r"c:\Docs\Phishing_Detection\extension.zip")

def package():
    print(f"Packaging Chrome Extension into: {OUTPUT_ZIP.name}")
    print("=" * 60)

    if OUTPUT_ZIP.exists():
        OUTPUT_ZIP.unlink()

    included_files = []
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(EXTENSION_DIR):
            for file in files:
                full_path = Path(root) / file
                rel_path = full_path.relative_to(EXTENSION_DIR)
                # Skip any git, temporary or hidden files
                if file.startswith(".") or file.endswith(".tmp") or file.endswith(".bak"):
                    continue
                zf.write(full_path, arcname=str(rel_path))
                included_files.append(str(rel_path))

    print(f"[SUCCESS] Packaged {len(included_files)} files into {OUTPUT_ZIP}:")
    for f in included_files:
        print(f"  + {f}")
    size_kb = OUTPUT_ZIP.stat().st_size / 1024.0
    print(f"Total zip size: {size_kb:.2f} KB")

if __name__ == "__main__":
    package()
