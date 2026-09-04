"""
Tampering Demonstration Helper Script.
Demonstrates how subtle changes to an image file break its cryptographic SHA-256 fingerprint,
proving the tamper-evidence of blockchain registration.
"""
import os
import sys
import shutil
import argparse
from utils.hashing import hash_file

# Ensure Windows PowerShell handles UTF-8 checkmarks and symbols cleanly
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def parse_args():
    parser = argparse.ArgumentParser(
        description="Tamper demonstration helper: subtly modifies an image file to trigger verification failure."
    )
    parser.add_argument(
        "--image",
        "-i",
        type=str,
        default="output/matched_image.jpg",
        help="Path to the image to tamper with (default: output/matched_image.jpg)"
    )
    parser.add_argument(
        "--restore",
        action="store_true",
        help="Restore the original image from the backup created before tampering"
    )
    return parser.parse_args()


def tamper_file():
    args = parse_args()
    image_path = os.path.abspath(args.image)
    backup_path = image_path + ".backup"

    if args.restore:
        if not os.path.exists(backup_path):
            print(f"[ERROR] Backup file not found at {backup_path}")
            sys.exit(1)
        shutil.copyfile(backup_path, image_path)
        os.remove(backup_path)
        print("=" * 60)
        print("  FILE RESTORED TO ORIGINAL")
        print("=" * 60)
        print(f"Target:        {args.image}")
        print(f"Restored Hash: {hash_file(image_path)}")
        print("You can now rerun verify.py to see VERIFICATION PASSED.")
        sys.exit(0)

    if not os.path.exists(image_path):
        print(f"[ERROR] Target file not found: {args.image}")
        sys.exit(1)

    # 1. Compute original hash
    orig_hash = hash_file(image_path)

    # 2. Backup original file
    shutil.copyfile(image_path, backup_path)

    # 3. Apply subtle modification (append a single byte or comment tag to bytes)
    with open(image_path, "ab") as f:
        f.write(b"\x00TAMPERED_CONTENT_DEMO_HH_GOA_2026\x00")

    # 4. Compute new hash
    new_hash = hash_file(image_path)

    print("=" * 60)
    print("  TAMPERING SIMULATION COMPLETE")
    print("=" * 60)
    print(f"File Modified: {args.image}")
    print(f"Original Hash: {orig_hash}")
    print(f"Tampered Hash: {new_hash}")
    print("-" * 60)
    print("The file's byte contents have been altered.")
    print("Notice that the SHA-256 fingerprint has completely changed.")
    print("\nNext step: Run verification to see the tamper detection in action:")
    print(f"  python verify.py --image {args.image}")
    print("\nTo restore the original un-tampered image later:")
    print(f"  python tamper_demo.py --image {args.image} --restore")
    print("=" * 60)


if __name__ == "__main__":
    tamper_file()
