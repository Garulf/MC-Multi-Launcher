from flox import Flox
from flox.string_matcher import string_matcher

from mc_launcher.launcher import check_installed_launchers


def select_launcher(plugin: Flox):
    for launcher in check_installed_launchers():
        plugin.add_item(
            title=launcher,
            subtitle='Select this launcher to set it as the default',
            method='set_launcher_dir',
            parameters=[str(launcher.path)],
        )
    plugin.add_item(
        title='Select a launcher directory',
        subtitle='Select this to set a custom launcher directory',
        method='open_file_dialog'
    )


def query_instances(plugin: Flox, query: str):
    for instance in plugin.mc_launcher.instances():
        match = string_matcher(query, instance.name)
        score = match[-1] if match else 0
        plugin.add_item(
            title=instance.name,
            subtitle=str(instance.path),
            icon=str(instance.icon),
            score=int(score),
            method='default_action',
            parameters=[str(instance.path)],
        )
