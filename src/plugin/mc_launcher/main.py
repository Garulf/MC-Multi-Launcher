import datetime
import traceback
from typing import AsyncIterator, List, Optional, Tuple

import humanize
from pyflowlauncher import Plugin, Result, api

from mc_launcher.icons import COBWEB, DEFAULT
from mc_launcher.instance import Instance
from mc_launcher.launcher import MCLauncher, detect_launchers, launcher_from_path

SETTING_LAUNCHER_DIR = "launcher_dir"

plugin = Plugin()


@plugin.on_method
async def query(query: str) -> AsyncIterator[Result]:
    launchers, problem = _launchers()
    if problem is not None:
        yield problem
        return
    entries = _instances_by_recency(launchers)
    if not entries:
        yield _no_instances_result(launchers[0])
        return
    show_launcher_name = len(launchers) > 1
    for rank, (mc, instance) in enumerate(entries):
        result = _instance_result(mc, instance, show_launcher_name)
        if query:
            match = await plugin.launcher.api.fuzzy_search(query, instance.name)
            if not match.matched:
                continue
            result.score = int(match.score)
            result.title_highlight_data = match.index_list
        else:
            result.score = len(entries) - rank
        yield result


@plugin.on_method
def launch_instance(executable: str, instance_id: str):
    mc = launcher_from_path(executable)
    if mc is None:
        return api.show_msg("Launcher not found", executable, str(COBWEB))
    try:
        mc.launch(instance_id)
    except OSError as error:
        return api.show_msg(f"Could not start {mc.name}", str(error), str(COBWEB))
    return None


@plugin.on_method
def open_launcher(executable: str):
    mc = launcher_from_path(executable)
    if mc is None:
        return api.show_msg("Launcher not found", executable, str(COBWEB))
    try:
        mc.open()
    except OSError as error:
        return api.show_msg(f"Could not start {mc.name}", str(error), str(COBWEB))
    return None


@plugin.on_except(Exception)
def unexpected_error(error: Exception) -> Result:
    return Result(
        title="Minecraft Multi Launcher ran into an error",
        subtitle=f"{type(error).__name__}: {error}",
        icon=str(COBWEB),
        copy_text="".join(traceback.format_exception(type(error), error, error.__traceback__)),
    )


def _launchers() -> Tuple[List[MCLauncher], Optional[Result]]:
    custom_path = str(plugin.settings.get(SETTING_LAUNCHER_DIR) or "").strip()
    if custom_path:
        mc = launcher_from_path(custom_path)
        if mc is None:
            return [], _settings_result(
                "Launcher not found",
                f"No MultiMC, PolyMC or Prism Launcher in {custom_path}. Press Enter to fix the path.",
            )
        return [mc], None
    launchers = detect_launchers()
    if not launchers:
        return [], _settings_result(
            "No launcher found",
            "Press Enter to set the folder of your MultiMC, PolyMC or Prism Launcher install.",
        )
    return launchers, None


def _instances_by_recency(launchers: List[MCLauncher]) -> List[Tuple[MCLauncher, Instance]]:
    entries = [(mc, instance) for mc in launchers for instance in mc.instances()]
    never = datetime.datetime.min
    return sorted(entries, key=lambda entry: entry[1].last_launch or never, reverse=True)


def _instance_result(mc: MCLauncher, instance: Instance, show_launcher_name: bool) -> Result:
    details = [_last_played(instance)]
    if instance.play_time:
        details.append(f"Played for {humanize.naturaldelta(instance.play_time)}")
    if show_launcher_name:
        details.append(mc.name)
    open_launcher_item = Result(title=f"Open {mc.name}", subtitle=str(mc.install_dir), icon=str(DEFAULT))
    open_launcher_item.add_action(open_launcher, [str(mc.executable)])
    open_folder_item = Result(title="Open instance folder", subtitle=str(instance.path), icon=str(DEFAULT))
    open_folder_item.add_action(api.open_directory(str(instance.path)))
    result = Result(
        title=instance.name,
        subtitle="  ·  ".join(details),
        icon=str(instance.icon(mc.icons_dir)),
        context_data=[open_launcher_item, open_folder_item],
    )
    return result.add_action(launch_instance, [str(mc.executable), instance.id])


def _last_played(instance: Instance) -> str:
    if instance.last_launch is None:
        return "Never played"
    return f"Last played {humanize.naturaltime(instance.last_launch)}"


def _no_instances_result(mc: MCLauncher) -> Result:
    result = Result(
        title="No instances found",
        subtitle=f"Press Enter to open {mc.name} and create one",
        icon=str(COBWEB),
    )
    return result.add_action(open_launcher, [str(mc.executable)])


def _settings_result(title: str, subtitle: str) -> Result:
    return Result(title=title, subtitle=subtitle, icon=str(COBWEB)).add_action(api.open_setting_dialog())
