import datetime
from pathlib import Path
from typing import Optional, Union

from mc_launcher import config
from mc_launcher.icons import DEFAULT, ICONS

CONFIG_FILE = "instance.cfg"
ICON_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".ico")
GAME_DIRS = (".minecraft", "minecraft")


class Instance:
    """A Minecraft instance folder managed by MultiMC, PolyMC or Prism Launcher."""

    def __init__(self, path: Union[str, Path]) -> None:
        self.path = Path(path)
        config_file = self.path / CONFIG_FILE
        if not config_file.is_file():
            raise FileNotFoundError(f"Instance config file not found: {config_file}")
        self.config = config.load(config_file)

    @property
    def id(self) -> str:
        return self.path.name

    @property
    def name(self) -> str:
        return self.config.get("name") or self.id

    @property
    def last_launch(self) -> Optional[datetime.datetime]:
        millis = _to_int(self.config.get("lastLaunchTime"))
        if not millis:
            return None
        try:
            return datetime.datetime.fromtimestamp(millis / 1000)
        except (OverflowError, OSError, ValueError):
            return None

    @property
    def play_time(self) -> Optional[datetime.timedelta]:
        seconds = _to_int(self.config.get("totalTimePlayed"))
        if seconds is None:
            return None
        return datetime.timedelta(seconds=seconds)

    def icon(self, icons_dir: Optional[Path] = None) -> Path:
        key = self.config.get("iconKey", "")
        if key in ICONS:
            return ICONS[key]
        if key and icons_dir is not None:
            for extension in ICON_EXTENSIONS:
                custom = icons_dir / f"{key}{extension}"
                if custom.is_file():
                    return custom
        for game_dir in GAME_DIRS:
            pack_icon = self.path / game_dir / "icon.png"
            if pack_icon.is_file():
                return pack_icon
        return DEFAULT


def _to_int(value: Optional[str]) -> Optional[int]:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
