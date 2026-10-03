"""Stage the plugin with its dependencies and optionally zip it for release."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILES = ("plugin.json", "icon.png", "SettingsTemplate.yaml")


def stage(dest: Path) -> Path:
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(ROOT / "src", dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "site-packages"))
    for name in DATA_FILES:
        shutil.copy2(ROOT / "data" / name, dest / name)
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "--no-compile",
         "--requirement", str(ROOT / "requirements.txt"),
         "--target", str(dest / "plugin" / "site-packages")],
        check=True,
    )
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, default=ROOT / "build" / "plugin", help="staging directory")
    parser.add_argument("--zip", type=Path, help="write a release archive to this path")
    args = parser.parse_args()

    staged = stage(args.dest)
    print(f"Staged {staged}")
    if args.zip:
        archive = shutil.make_archive(str(args.zip.with_suffix("")), "zip", staged)
        print(f"Wrote {archive}")


if __name__ == "__main__":
    main()
