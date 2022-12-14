from pathlib import Path
import zipfile
import os

from install import DIST_DIR, get_plugin_name


def package_plugin(dir: Path = Path(DIST_DIR)) -> None:
    plugin_name = get_plugin_name()
    # zip contents of directory
    with zipfile.ZipFile(f"{plugin_name}.zip", "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(dir):
            for file in files:
                zip_file.write(os.path.join(root, file),
                               os.path.relpath(os.path.join(root, file), dir))


def main():
    package_plugin()


if __name__ == '__main__':
    main()
    print("\a")
