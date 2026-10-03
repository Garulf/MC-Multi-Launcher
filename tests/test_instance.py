import datetime

import pytest

from mc_launcher.icons import DEFAULT, ICONS
from mc_launcher.instance import Instance


def make_instance(tmp_path, cfg, folder="Base"):
    path = tmp_path / folder
    path.mkdir()
    (path / "instance.cfg").write_text(cfg, encoding="utf-8")
    return path


def test_reads_name_and_id(tmp_path):
    instance = Instance(make_instance(tmp_path, "[General]\nname=My Base\n", folder="mybase"))
    assert instance.name == "My Base"
    assert instance.id == "mybase"


def test_name_falls_back_to_folder(tmp_path):
    instance = Instance(make_instance(tmp_path, "iconKey=steve\n", folder="nameless"))
    assert instance.name == "nameless"


def test_missing_config_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        Instance(tmp_path)


def test_play_stats(tmp_path):
    launched = datetime.datetime(2026, 1, 2, 3, 4, 5)
    millis = int(launched.timestamp() * 1000)
    instance = Instance(
        make_instance(tmp_path, f"lastLaunchTime={millis}\ntotalTimePlayed=3600\n")
    )
    assert instance.last_launch == launched
    assert instance.play_time == datetime.timedelta(hours=1)


def test_missing_or_garbage_stats_are_none(tmp_path):
    instance = Instance(make_instance(tmp_path, "lastLaunchTime=abc\ntotalTimePlayed=\n"))
    assert instance.last_launch is None
    assert instance.play_time is None


def test_zero_launch_time_means_never_played(tmp_path):
    instance = Instance(make_instance(tmp_path, "lastLaunchTime=0\n"))
    assert instance.last_launch is None


def test_builtin_icon(tmp_path):
    instance = Instance(make_instance(tmp_path, "iconKey=creeper\n"))
    assert instance.icon() == ICONS["creeper"]


def test_custom_icon_from_launcher_icons_dir(tmp_path):
    icons_dir = tmp_path / "icons"
    icons_dir.mkdir()
    (icons_dir / "mypack.jpg").write_bytes(b"jpg")
    instance = Instance(make_instance(tmp_path, "iconKey=mypack\n"))
    assert instance.icon(icons_dir) == icons_dir / "mypack.jpg"


def test_pack_icon_inside_instance(tmp_path):
    path = make_instance(tmp_path, "iconKey=unknown\n")
    (path / ".minecraft").mkdir()
    (path / ".minecraft" / "icon.png").write_bytes(b"png")
    assert Instance(path).icon() == path / ".minecraft" / "icon.png"


def test_unknown_icon_uses_default(tmp_path):
    instance = Instance(make_instance(tmp_path, "iconKey=unknown\n"))
    assert instance.icon(tmp_path / "missing") == DEFAULT
