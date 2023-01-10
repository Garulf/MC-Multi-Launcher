from flox import Flox
from flox.string_matcher import string_matcher

from mc_launcher.launcher import check_installed_launchers
from mc_launcher.icons import COBWEB


def select_launcher(plugin: Flox, query: str):
    for launcher in check_installed_launchers():
        plugin.add_item(
            title=launcher.name,
            subtitle='Select this launcher to set it as the default',
            method='set_launcher_dir',
            parameters=[str(launcher.path)],
        )
    plugin.add_item(
        title='Please set your launcher path in the settings',
        subtitle='Click here to open the settings',
        method='open_setting_dialog'
    )
    if len(query) > 0:
        plugin.add_item(
            title='Set launcher path to "{}"'.format(query),
            subtitle='Click here to set the launcher path to "{}"'.format(
                query),
            method='set_launcher_dir',
            parameters=[query],
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
    no_instances(plugin)

def no_instances(plugin: Flox):
    if len(plugin._results) == 0:
        plugin.add_item(
            title='No instances found',
            subtitle='Please create an instance in your launcher',
            icon=str(COBWEB),
            method='open_launcher'
        )