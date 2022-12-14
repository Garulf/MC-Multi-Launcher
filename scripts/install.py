import json
from shutil import copytree
import os
from pathlib import Path

from manifest import FlowLauncherManifest
from config import load_config, DEFAULT_MANIFEST, DEFAULT_LAUNCHER_DIR, DEFAULT_SOURCE_DIR


DIST_DIR = "plugin.dist"


def get_plugin_name(plugin_manifest: str = DEFAULT_MANIFEST, directory: str = DEFAULT_SOURCE_DIR) -> str:
    full_path = Path(directory).joinpath(plugin_manifest)
    with open(full_path, "r") as f:
        return json.load(f)["Name"]


def move_plugin(launcher_plugins_dir: str = DEFAULT_LAUNCHER_DIR, plugin_manifest_path: str = DEFAULT_MANIFEST) -> None:
    plugin_manifest = FlowLauncherManifest.from_file(plugin_manifest_path)
    plugin_dir = launcher_plugins_dir.joinpath(plugin_manifest.Name)
    build_dir = DIST_DIR
    copytree(build_dir, plugin_dir, dirs_exist_ok=True)


def main():
    config = load_config()
    move_plugin(config.launcher_plugin_dir, config.manifest)
    print("Plugin installed")


if __name__ == '__main__':
    main()
    print("\a")
