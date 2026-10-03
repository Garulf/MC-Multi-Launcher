import os
from pathlib import Path
from subprocess import DEVNULL, Popen
from typing import Dict, Iterator, List, NamedTuple, Optional, Union

from mc_launcher import config
from mc_launcher.instance import Instance

PORTABLE_MARKER = "portable.txt"


class Kind(NamedTuple):
    name: str
    folder: str
    config_file: str
    always_portable: bool = False


KINDS: Dict[str, Kind] = {
    "prismlauncher.exe": Kind("Prism Launcher", "PrismLauncher", "prismlauncher.cfg"),
    "polymc.exe": Kind("PolyMC", "PolyMC", "polymc.cfg"),
    "multimc.exe": Kind("MultiMC", "MultiMC", "multimc.cfg", always_portable=True),
}

INSTALL_FOLDERS = ("PrismLauncher", "Prism Launcher", "PolyMC", "MultiMC")
SCOOP_APPS = ("prismlauncher", "polymc", "multimc")


class MCLauncher:
    """An installed MultiMC, PolyMC or Prism Launcher, identified by its executable."""

    def __init__(self, executable: Path) -> None:
        self.executable = executable
        self.kind = KINDS[executable.name.lower()]
        self.data_dir = self._find_data_dir()
        config_file = self.data_dir / self.kind.config_file
        self.config = config.load(config_file) if config_file.is_file() else {}

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MCLauncher) and _key(self.executable) == _key(other.executable)

    def __hash__(self) -> int:
        return hash(_key(self.executable))

    def __repr__(self) -> str:
        return f"MCLauncher({str(self.executable)!r})"

    @property
    def name(self) -> str:
        return self.kind.name

    @property
    def install_dir(self) -> Path:
        return self.executable.parent

    @property
    def instance_dir(self) -> Path:
        return self._data_path("InstanceDir", "instances")

    @property
    def icons_dir(self) -> Path:
        return self._data_path("IconsDir", "icons")

    def instances(self) -> List[Instance]:
        try:
            folders = sorted(self.instance_dir.iterdir())
        except OSError:
            return []
        instances = []
        for folder in folders:
            try:
                instances.append(Instance(folder))
            except OSError:
                continue
        return instances

    def launch(self, instance_id: str) -> None:
        self._start("--launch", instance_id)

    def open(self) -> None:
        self._start()

    def _start(self, *args: str) -> None:
        # stdout is Flow Launcher's JSON-RPC pipe, so the launcher must not inherit it.
        Popen([str(self.executable), *args], cwd=self.install_dir, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)

    def _find_data_dir(self) -> Path:
        user_dir = _env_path("APPDATA", self.kind.folder)
        portable = self.kind.always_portable or (self.install_dir / PORTABLE_MARKER).is_file()
        candidates = [self.install_dir] if portable or user_dir is None else [self.install_dir, user_dir]
        for candidate in candidates:
            if (candidate / self.kind.config_file).is_file():
                return candidate
        return candidates[-1]

    def _data_path(self, key: str, default: str) -> Path:
        path = Path(self.config.get(key) or default)
        return path if path.is_absolute() else self.data_dir / path


def launcher_from_path(path: Union[str, Path]) -> Optional[MCLauncher]:
    """Build a launcher from a folder or .exe path; None if no known launcher is there."""
    text = str(path).strip().strip('"')
    if not text:
        return None
    executable = _find_executable(Path(text))
    return MCLauncher(executable) if executable else None


def detect_launchers() -> List[MCLauncher]:
    """Every launcher found in the usual install locations, without duplicates."""
    found: List[MCLauncher] = []
    for folder in _install_candidates():
        mc = launcher_from_path(folder)
        if mc is not None and mc not in found:
            found.append(mc)
    return found


def _find_executable(path: Path) -> Optional[Path]:
    try:
        if path.is_file():
            return path if path.name.lower() in KINDS else None
        if path.is_dir():
            return next((child for child in sorted(path.iterdir()) if child.name.lower() in KINDS and child.is_file()), None)
    except OSError:
        pass
    return None


def _install_candidates() -> Iterator[Path]:
    for var, subdir in (("LOCALAPPDATA", "Programs"), ("LOCALAPPDATA", ""), ("PROGRAMFILES", ""),
                        ("PROGRAMFILES(X86)", ""), ("APPDATA", "")):
        base = _env_path(var, subdir)
        if base is not None:
            for folder in INSTALL_FOLDERS:
                yield base / folder
    scoop = _env_path("USERPROFILE", "scoop")
    if scoop is not None:
        for app in SCOOP_APPS:
            yield scoop / "apps" / app / "current"


def _env_path(var: str, *parts: str) -> Optional[Path]:
    value = os.getenv(var)
    return Path(value, *parts) if value else None


def _key(path: Path) -> str:
    return os.path.normcase(str(path.resolve()))
