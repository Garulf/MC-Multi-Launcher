import datetime
from typing import Union
import humanize
from pathlib import Path

from mc_launcher import config
from mc_launcher.icons import ICONS

CONFIG_FILE: str = 'instance.cfg'


class Instance:
    """A Minecraft instance"""

    def __init__(self, path) -> None:
        self.path = path
        try:
            self.config = config.load(Path(self.path).joinpath(CONFIG_FILE))
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Instance config file not found: {self.path}")

    @property
    def name(self) -> str:
        return self.config.get('name')

    @property
    def icon_key(self) -> str:
        return self.config.get('iconKey')

    @property
    def icon(self) -> Union[str, None]:
        _icon = ICONS.get(self.icon_key, None)
        if _icon:
            return _icon
        instance_icon_png = Path(self.path).joinpath('minecraft', 'icon.png')
        if instance_icon_png.exists():
            return str(instance_icon_png)
        return ICONS.get('default')

    @property
    def last_played(self) -> str:
        lastLaunchTime = self.config.get('lastLaunchTime')
        if lastLaunchTime:
            dt = datetime.datetime.fromtimestamp(int(lastLaunchTime) / 1000)
            return humanize.naturaltime(dt)
        return 'Never Played'

    @property
    def total_time_played(self) -> str:
        totalTimePlayed = self.config.get('totalTimePlayed')
        if totalTimePlayed:
            return humanize.naturaldelta(datetime.timedelta(
                seconds=int(totalTimePlayed)), minimum_unit='seconds')
        return 'Never Played'
