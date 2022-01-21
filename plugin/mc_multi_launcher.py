from pathlib import Path as p
from subprocess import Popen, call, PIPE
import re

from flox import Flox

MC_EXE = 'MultiMC.exe'
MMC_TEMP_PATH = '_MMC_TEMP'
MULTIMC_CFG = "multimc.cfg"
INSTANCE_CFG = 'instance.cfg'
INSTANCE_MODLIST = 'modlist.html'
ICON_NAME = "icon.png"

class MCMultiLauncher(Flox):

    def __init__(self):
        self.mmc_dir = self.load_config("settings.cfg")["MultiMCLocation"]
        self.config_path = p(self.mmc_dir).joinpath(MULTIMC_CFG)
        self.config = self.load_config(self.config_path)
        self.instance_dir = p(self.mmc_dir).joinpath(self.config["InstanceDir"])
        self.icons_dir = p(self.mmc_dir).joinpath(self.config["IconsDir"])
        super().__init__()

    def find_icon(self, instance_dir):
        if p(instance_dir).joinpath("minecraft", ICON_NAME).exists() or p(instance_dir).joinpath(".minecraft", ICON_NAME).exists():
            self.logger.info("test")
            return p(instance_dir).joinpath("minecraft", ICON_NAME)
        icon_key = self.load_config(p(self.instance_dir).joinpath(instance_dir, INSTANCE_CFG)).get("iconKey")
        self.logger.info(icon_key)
        icon_path = p(self.icons_dir).joinpath(icon_key)
        self.logger.info(icon_path)
        if icon_path.exists() and str(icon_path).endswith(('.png', '.jpg', '.jpeg')):
            return icon_path
        return self.icon
        

    def grab_instances(self):
        instances = []
        for instance in p(self.instance_dir).iterdir():
            if instance == p(self.instance_dir).joinpath(MMC_TEMP_PATH) or not instance.is_dir():
                continue
            
            instance_config_path = p(self.instance_dir).joinpath(instance, INSTANCE_CFG)
            config = self.load_config(instance_config_path)
            instances.append(
                {
                    "name": config["name"],
                    "icon": str(self.find_icon(instance)),
                    "path": str(instance)
                }
            )
        return instances

    def load_config(self, path):
        with open(path, "r") as f:
            props = dict(line.strip().split('=', 1) for line in f)
        return props

    def query(self, query):
        instances = self.grab_instances()
        for instance in instances:
            self.add_item(
                title=instance["name"],
                subtitle=instance["path"],
                icon=instance["icon"],
                method="launch_instance",
                parameters=[instance["name"]]
            )

    def context(self, data):
        pass

    def launch_instance(self, instance):
        Popen(f'{MC_EXE} -l "{instance}"')

if __name__ == "__main__":
    MCMultiLauncher()