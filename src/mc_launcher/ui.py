from flox import Flox
from mc_launcher.launcher import MCLauncher
from mc_launcher.instance import Instance
from mc_launcher.results import select_launcher, query_instances

SETTINGS_LAUNCHER_DIR = 'launcher_dir'


class MCMultiLauncher(Flox):

    def __init__(self):
        """Setup settings and create the launcher object"""
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
            return select_launcher(self, query)
        return query_instances(self, query)

    def set_launcher_dir(self, launcher_path: str):
        launcher = MCLauncher(launcher_path)
        if launcher.executable():
            self.settings['launcher_dir'] = str(launcher_path)
            self.change_query(self.action_keyword, True)
        else:
            self.show_msg('Invalid launcher path',
                          launcher_path, ico_path=self.icon)

    def default_action(self, instance_path: str):
        """This is used when a user selects a result"""
        instance = Instance(instance_path)
        self.mc_launcher.launch_instance(instance)
        self.show_msg('Launching instance', instance.name)
