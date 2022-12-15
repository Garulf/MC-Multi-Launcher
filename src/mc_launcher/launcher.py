import os
from pathlib import Path
from typing import List
from subprocess import Popen

from mc_launcher.instance import Instance
from mc_launcher import config


# C:\Users\<user>\AppData\Local\Programs\PrismLauncher
# C:\Users\<user>\AppData\Local\Programs\PolyMC
LOCAL = Path(os.getenv('LOCALAPPDATA'))
ROAMING = Path(os.getenv('APPDATA'))
DEFAULT_INSTANCE_DIR: str = 'instances'

# Launcher Executable file names
MULTIMC_EXE = 'multimc.exe'
POLYMC_EXE = 'polymc.exe'
PRISM_LAUNCHER_EXE = 'prismlauncher.exe'

LAUNCHER_EXES = [
    MULTIMC_EXE,
    POLYMC_EXE,
    PRISM_LAUNCHER_EXE
]

# Launcher Folder names
MULTIMC_FOLDER = 'MultiMC'
POLYMC_FOLDER = 'PolyMC'
PRISM_LAUNCHER_FOLDER = 'PrismLauncher'

LAUNCHER_FOLDERS = [
    MULTIMC_FOLDER,
    POLYMC_FOLDER,
    PRISM_LAUNCHER_FOLDER
]

# Launcher Config file names
MULTINC_CFG: str = 'multimc.cfg'
POLYMC_CFG: str = 'polymc.cfg'
PRISMLAUNCHER_CFG: str = 'prismlauncher.cfg'

LAUNCHER_CFGS = [
    MULTINC_CFG,
    POLYMC_CFG,
    PRISMLAUNCHER_CFG
]


def check_installed_launchers() -> List['MCLauncher']:
    """Check if any of the launchers are installed"""
    installed_launchers = []
    for launcher in LAUNCHER_FOLDERS:
        launcher_path = Path(LOCAL).joinpath('Programs', launcher)
        if launcher_path.exists():
            installed_launchers.append(
                MCLauncher(launcher_path, name=launcher))
    return installed_launchers


class MCLauncher:

    def __init__(self, path: Path, name: str = None):
        self.path = path
        self.name = name
        self.config = config.load(self._config())

    def _config(self):
        _path = self.path
        if str(self.path).startswith(str(LOCAL)):
            _path = ROAMING.joinpath(Path(self.path).name)
        return Path(_path).glob('*.cfg').__next__()

    def executable(self):
        executables = [exe for exe in Path(self.path).glob('*.exe')]
        for exe in executables:
            if exe.name.lower() in LAUNCHER_EXES:
                return exe

    @property
    def instance_dir(self) -> Path:
        instance_dir = self.config.get('InstanceDir')
        if instance_dir == DEFAULT_INSTANCE_DIR:
            return Path(self.path).joinpath(instance_dir)
        return Path(instance_dir)

    def instances(self) -> List[Instance]:
        instances = []
        for instance in self.instance_dir.iterdir():
            try:
                instances.append(Instance(instance))
            except FileNotFoundError:
                pass
        return instances

    def launch_instance(self, instance: Instance):
        exe = self.executable()
        path_to_exe = Path(self.path).joinpath(exe)
        # Instances can have the same name so we launch using the folder name
        cmd = [str(exe), '-l', Path(instance.path).name]
        Popen(cmd, executable=path_to_exe, cwd=self.path)


class InstalledLauncher(MCLauncher):

    def __init__(self, path):
        super().__init__(path)
        _name = Path(self.path).stem
        self.config = ROAMING.joinpath(_name, f"{_name}.cfg")
