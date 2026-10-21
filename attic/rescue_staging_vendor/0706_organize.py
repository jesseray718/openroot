#!/data/data/com.termux/files/usr/bin/python3
import os
import shutil
from pathlib import Path

def organize_files(directory, dry_run=True):
    categories = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf'],
        'code': ['.py', '.js', '.ts', '.html', '.css', '.java', '.c', '.cpp', '.go'],
        'models': ['.pth', '.h5', '.onnx', '.bin', '.gguf', '.safetensors'],
        'archives': ['.zip', '.tar', '.gz', '.rar', '.7z'],
        'media': ['.mp4', '.mkv', '.avi', '.mp3', '.wav', '.flac']
    }

    folder = Path(directory).expanduser()
    organized_count = 0

    print(f"{'[DRY RUN] ' if dry_run else ''}Organizing files in: {folder}")

    for item in folder.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            ext = item.suffix.lower()
            moved = False

            for category, extensions in categories.items():
                if ext in extensions:
                    target_dir = folder / category
                    target_dir.mkdir(exist_ok=True)

                    if not dry_run:
                        shutil.move(str(item), str(target_dir / item.name))
                        print(f"  Moved {item.name} -> {category}/")
                    else:
                        print(f"  Would move {item.name} -> {category}/")

                    organized_count += 1
                    moved = True
                    break

            if not moved:
                others_dir = folder / 'others'
                others_dir.mkdir(exist_ok=True)

                if not dry_run:
                    shutil.move(str(item), str(others_dir / item.name))
                    print(f"  Moved {item.name} -> others/")
                else:
                    print(f"  Would move {item.name} -> others/")

                organized_count += 1

    print(f"\nTotal files organized: {organized_count}")

if __name__ == "__main__":
    # DRY RUN first — no actual changes
    organize_files("~", dry_run=True)
    # To actually move files, run:
    # organize_files("~", dry_run=False)
