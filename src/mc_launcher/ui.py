from flox import Flox
from mc_launcher.launcher import MCLauncher
from mc_launcher.instance import Instance
from mc_launcher.results import select_launcher, query_instances
from mc_launcher.actions import OpenFileDialog

SETTINGS_LAUNCHER_DIR = 'launcher_dir'


class MCMultiLauncher(Flox):

    def __init__(self):
        """Setup settings and create the launcher object"""
        self.open_file_dialog = OpenFileDialog(self)
        self.launcher_dir = self.settings.get(SETTINGS_LAUNCHER_DIR)
        if self.launcher_dir:
            self.mc_launcher = MCLauncher(self.launcher_dir)

    def __del__(self):
        """Override Flox's del method"""
        pass

    def query(self, query):
        # Check if the launcher dir is set
        if not self.launcher_dir:
            # If not, ask the user to select the launcher dir
            return select_launcher(self)
        return query_instances(self, query)

    def set_launcher_dir(self, launcher_path: str):
        self.settings['launcher_dir'] = str(launcher_path)

    def default_action(self, instance_path: str):
        """This is used when a user selects a result"""
        instance = Instance(instance_path)
        self.mc_launcher.launch_instance(instance)
        self.notify('Launching instance', instance.name)
