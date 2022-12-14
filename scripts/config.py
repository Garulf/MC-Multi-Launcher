import json
import os
from pathlib import Path
from typing import TypedDict, List
from dataclasses import dataclass, field

ROAMING = Path(os.getenv("APPDATA"))
DEFAULT_LAUNCHER_DIR = ROAMING.joinpath("FlowLauncher", "Plugins")
DEFAULT_SOURCE_DIR = "src"
DEFAULT_MAIN_FILE = "plugin.py"
DEFAULT_VIRTUAL_ENV = "venv"
DEFAULT_REQUIREMENTS_FILE = "requirements.txt"
DEFAULT_REQUIREMENTS_DEV_FILE = "requirements-dev.txt"
DEFAULT_ICON = "icon.png"
DEFAULT_MANIFEST = "plugin.json"


class DataFile(TypedDict):
    src: str
    dest: str


@dataclass
class Config:
    source_dir: str = DEFAULT_SOURCE_DIR
    main_file: str = DEFAULT_MAIN_FILE
    data_files: List[DataFile] = field(default_factory=list)
    icon: str = DEFAULT_ICON
    virtual_env: str = DEFAULT_VIRTUAL_ENV
    requirements: str = DEFAULT_REQUIREMENTS_FILE
    requirements_dev: str = DEFAULT_REQUIREMENTS_DEV_FILE
    manifest: str = DEFAULT_MANIFEST
    launcher_plugin_dir: str = DEFAULT_LAUNCHER_DIR

    def __post_init__(self):
        for data_file in self.data_files:
            if "dest" not in data_file.keys():
                data_file["dest"] = "."
        if not Path(self.source_dir).is_absolute():
            self.source_dir = Path.cwd().joinpath(self.source_dir)
        if not Path(self.main_file).is_absolute():
            self.main_file = Path(self.source_dir).joinpath(self.main_file)
        if not Path(self.icon).is_absolute():
            self.icon = Path(self.source_dir).joinpath(self.icon)
        if not Path(self.manifest).is_absolute():
            self.manifest = Path(self.source_dir).joinpath(self.manifest)

    def _resolve_path(self, path: str) -> Path:
        base_path = Path(self.source_dir)
        if self.source_dir not in path:
            base_path = Path.cwd()
        return base_path.joinpath(path)


def load_config() -> Config:
    print("Loading config")
    with open("project.json", "r") as f:
        return Config(**json.load(f))
