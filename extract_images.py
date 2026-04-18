"""
extract_images.py
-----------------
Extracts all base64-embedded images from index.html,
saves them as real files in an images/ folder,
and rewrites index.html with src="images/..." references.

HOW TO USE:
1. Copy this file to  C:\JovensYoga\site\
2. Open a terminal (PowerShell or cmd) in that folder
3. Run:  python extract_images.py
4. Check the images/ folder — your images will be there
5. index.html will now be ~50-100KB instead of 10MB
"""

import re
import os
import base64
import shutil

INPUT_FILE  = "index.html"
OUTPUT_FILE = "index.html"          # overwrites in place (backup made first)
IMAGES_DIR  = "images"
BACKUP_FILE = "index_backup_original.html"

# ── MIME type → file extension map ──────────────────────────────────────────
MIME_TO_EXT = {
    "image/jpeg"  : "jpg",
    "image/jpg"   : "jpg",
    "image/png"   : "png",
    "image/gif"   : "gif",
    "image/webp"  : "webp",
    "image/svg+xml": "svg",
    "image/avif"  : "avif",
}

def extract_images(html: str, images_dir: str) -> tuple[str, int]:
    os.makedirs(images_dir, exist_ok=True)
    counter = [0]

    # Matches:  data:image/jpeg;base64,/9j/4AAQ...
    pattern = re.compile(
        r'data:(image/[a-zA-Z+.-]+);base64,([A-Za-z0-9+/=]+)',
        re.IGNORECASE
    )

    def replace_match(m: re.Match) -> str:
        mime      = m.group(1).lower()
        b64_data  = m.group(2)
        ext       = MIME_TO_EXT.get(mime, "bin")
        counter[0] += 1
        filename  = f"image_{counter[0]:02d}.{ext}"
        filepath  = os.path.join(images_dir, filename)

        # Write the actual image file
        try:
            raw = base64.b64decode(b64_data)
            with open(filepath, "wb") as f:
                f.write(raw)
            size_kb = len(raw) // 1024
            print(f"  ✓ Saved {filename}  ({size_kb} KB)  [{mime}]")
        except Exception as e:
            print(f"  ✗ Could not decode image_{counter[0]:02d}: {e}")
            return m.group(0)   # leave original if decode fails

        return f"{images_dir}/{filename}"   # replacement src value

    new_html = pattern.sub(replace_match, html)
    return new_html, counter[0]


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: {INPUT_FILE} not found in current directory.")
        print(f"Make sure you run this script from C:\\JovensYoga\\site\\")
        return

    # Backup first
    shutil.copy2(INPUT_FILE, BACKUP_FILE)
    print(f"Backup saved → {BACKUP_FILE}")

    print(f"\nReading {INPUT_FILE} ...")
    with open(INPUT_FILE, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()

    original_kb = len(html.encode("utf-8")) // 1024
    print(f"Original size: {original_kb:,} KB\n")

    print(f"Extracting images to /{IMAGES_DIR}/ ...")
    new_html, count = extract_images(html, IMAGES_DIR)

    if count == 0:
        print("\nNo base64 images found. Nothing changed.")
        print("The file might already use external image references,")
        print("or images might be in CSS background-image properties.")
        return

    print(f"\nWriting updated {OUTPUT_FILE} ...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(new_html)

    new_kb = len(new_html.encode("utf-8")) // 1024
    print(f"\n{'='*50}")
    print(f"Done! {count} image(s) extracted.")
    print(f"  Before : {original_kb:,} KB")
    print(f"  After  : {new_kb:,} KB")
    print(f"  Saved  : {original_kb - new_kb:,} KB")
    print(f"\nNext steps:")
    print(f"  1. Open index.html in your browser — confirm it looks correct")
    print(f"  2. Replace placeholder images in images/ with your real photos")
    print(f"  3. Run deploy.ps1 to push to GitHub → Netlify")
    print(f"  4. Make sure Netlify deploys the images/ folder too")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()