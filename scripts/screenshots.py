"""Render the README screenshots with flow-render against a demo Prism Launcher install."""
import datetime
import os
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

from build import ROOT, stage

ASSETS = ROOT / ".github" / "assets"
THEME = "win11-dark"
DAY = datetime.timedelta(days=1)

DEMO_INSTANCES = (
    ("atm9", "All the Mods 9", "netherstar", datetime.timedelta(hours=2), 86 * 3600),
    ("create", "Create: Above and Beyond", "gear", DAY, 31 * 3600),
    ("vanilla", "Vanilla 1.21", "steve", 4 * DAY, 140 * 3600),
    ("skyblock", "Skyblock", "enderpearl", 15 * DAY, 9 * 3600),
    ("hardcore", "Hardcore", "creeper", None, 0),
)

SHOTS = {
    "screenshot": ["-q", "", "-m", "5", "-s", THEME],
    "search": ["-q", "create", "-m", "3", "-s", THEME],
    "install": ["-i", "-s", THEME],
    "hero": ["-q", "", "-m", "3", "-s", "hero-win11-dark", "-W", "1500", "-H", "560"],
}


def make_demo_install(home: Path) -> dict:
    install = home / "Local" / "Programs" / "PrismLauncher"
    install.mkdir(parents=True)
    (install / "prismlauncher.exe").write_bytes(b"")
    (install / "portable.txt").write_text("", encoding="utf-8")
    now = datetime.datetime.now()
    for folder, name, icon, last_played, seconds in DEMO_INSTANCES:
        instance = install / "instances" / folder
        instance.mkdir(parents=True)
        launched = int((now - last_played).timestamp() * 1000) if last_played else 0
        (instance / "instance.cfg").write_text(
            f"[General]\nname={name}\niconKey={icon}\nlastLaunchTime={launched}\ntotalTimePlayed={seconds}\n",
            encoding="utf-8",
        )
    return {**os.environ, "LOCALAPPDATA": str(home / "Local"), "APPDATA": str(home / "Roaming")}


def render(flow_render: list, plugin_dir: Path, args: list, env: dict, out_dir: Path) -> Path:
    out_dir.mkdir()
    subprocess.run([*flow_render, "-p", str(plugin_dir), "--hide-caret", "-o", str(out_dir), *args], env=env, check=True)
    (image,) = out_dir.glob("*.png")
    return image


def main() -> None:
    flow_render = shlex.split(os.environ.get("FLOW_RENDER", "flow-render"))
    ASSETS.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        plugin_dir = stage(tmp_path / "plugin")
        env = make_demo_install(tmp_path / "home")
        for name, args in SHOTS.items():
            image = render(flow_render, plugin_dir, args, env, tmp_path / name)
            shutil.move(str(image), ASSETS / f"{name}.png")
            print(f"Wrote {ASSETS / f'{name}.png'}")


if __name__ == "__main__":
    main()
