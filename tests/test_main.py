import asyncio
from pathlib import Path

import pytest

from mc_launcher import launcher, main
from mc_launcher.icons import ICONS

WINDOWS_ENV = ("LOCALAPPDATA", "APPDATA", "PROGRAMFILES", "PROGRAMFILES(X86)", "USERPROFILE")


@pytest.fixture(autouse=True)
def isolated(monkeypatch, tmp_path):
    for var in WINDOWS_ENV:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("APPDATA", str(tmp_path / "Roaming"))
    monkeypatch.setattr(main.plugin.launcher, "_settings", {})


def make_launcher(root: Path, exe: str, instances: dict) -> Path:
    root.mkdir(parents=True)
    (root / exe).write_bytes(b"MZ")
    (root / "portable.txt").write_text("", encoding="utf-8")
    for folder, cfg in instances.items():
        (root / "instances" / folder).mkdir(parents=True)
        (root / "instances" / folder / "instance.cfg").write_text(cfg, encoding="utf-8")
    return root


def call(method, *params):
    return asyncio.run(main.plugin._event_handler.trigger_event(method, *params))


def titles(response):
    return [result["Title"] for result in response["Result"]]


def use_setting(monkeypatch, value):
    monkeypatch.setattr(main.plugin.launcher, "_settings", {main.SETTING_LAUNCHER_DIR: value})


def test_no_launcher_points_to_settings():
    response = call("query", "")
    assert titles(response) == ["No launcher found"]
    assert response["Result"][0]["JsonRPCAction"]["Method"] == "Flow.Launcher.OpenSettingDialog"


def test_bad_custom_path_points_to_settings(monkeypatch, tmp_path):
    use_setting(monkeypatch, str(tmp_path / "nope"))
    response = call("query", "")
    assert titles(response) == ["Launcher not found"]
    assert str(tmp_path / "nope") in response["Result"][0]["SubTitle"]


def test_empty_query_lists_instances_most_recent_first(monkeypatch, tmp_path):
    root = make_launcher(tmp_path / "MultiMC", "MultiMC.exe", {
        "old": "name=Old\nlastLaunchTime=1000000000000\n",
        "new": "name=New\nlastLaunchTime=1700000000000\ntotalTimePlayed=7200\niconKey=creeper\n",
        "fresh": "name=Fresh\n",
    })
    use_setting(monkeypatch, str(root))

    response = call("query", "")

    results = sorted(response["Result"], key=lambda r: r["Score"], reverse=True)
    assert [r["Title"] for r in results] == ["New", "Old", "Fresh"]
    assert results[0]["SubTitle"].startswith("Last played")
    assert "Played for 2 hours" in results[0]["SubTitle"]
    assert results[0]["IcoPath"] == str(ICONS["creeper"])
    assert results[2]["SubTitle"] == "Never played"
    assert results[0]["JsonRPCAction"] == {
        "Method": "launch_instance",
        "Parameters": [str(root / "MultiMC.exe"), "new"],
        "DontHideAfterAction": False,
    }


def test_query_filters_and_highlights(monkeypatch, tmp_path):
    root = make_launcher(tmp_path / "MultiMC", "MultiMC.exe", {
        "atm": "name=All the Mods 9\n",
        "vanilla": "name=Vanilla\n",
    })
    use_setting(monkeypatch, str(root))

    response = call("query", "atm")

    assert titles(response) == ["All the Mods 9"]
    assert response["Result"][0]["TitleHighlightData"]


def test_detected_launchers_are_merged_and_labelled(monkeypatch, tmp_path):
    local = tmp_path / "Local"
    make_launcher(local / "Programs" / "PrismLauncher", "prismlauncher.exe", {"a": "name=Prism Pack\n"})
    make_launcher(local / "Programs" / "PolyMC", "polymc.exe", {"b": "name=Poly Pack\n"})
    monkeypatch.setenv("LOCALAPPDATA", str(local))

    response = call("query", "")

    subtitles = {r["Title"]: r["SubTitle"] for r in response["Result"]}
    assert subtitles["Prism Pack"].endswith("Prism Launcher")
    assert subtitles["Poly Pack"].endswith("PolyMC")


def test_context_menu_offers_launcher_and_folder(monkeypatch, tmp_path):
    root = make_launcher(tmp_path / "MultiMC", "MultiMC.exe", {"base": "name=Base\n"})
    use_setting(monkeypatch, str(root))
    context_data = call("query", "")["Result"][0]["ContextData"]

    menu = call("context_menu", [item.to_json() for item in context_data])

    assert titles(menu) == ["Open MultiMC", "Open instance folder"]


def test_no_instances_offers_to_open_launcher(monkeypatch, tmp_path):
    root = make_launcher(tmp_path / "MultiMC", "MultiMC.exe", {})
    use_setting(monkeypatch, str(root))
    response = call("query", "")
    assert titles(response) == ["No instances found"]
    assert response["Result"][0]["JsonRPCAction"]["Method"] == "open_launcher"


def test_launch_instance_starts_launcher(monkeypatch, tmp_path):
    root = make_launcher(tmp_path / "MultiMC", "MultiMC.exe", {"base": "name=Base\n"})
    calls = []
    monkeypatch.setattr(launcher, "Popen", lambda cmd, **kwargs: calls.append(cmd))

    assert call("launch_instance", str(root / "MultiMC.exe"), "base") is None
    assert calls == [[str(root / "MultiMC.exe"), "--launch", "base"]]


def test_launch_with_missing_launcher_shows_message(tmp_path):
    response = call("launch_instance", str(tmp_path / "gone.exe"), "base")
    assert response["Method"] == "Flow.Launcher.ShowMsg"


def test_unexpected_errors_become_a_result(monkeypatch):
    def boom():
        raise RuntimeError("kaboom")

    monkeypatch.setattr(main, "detect_launchers", boom)
    response = call("query", "")
    assert titles(response) == ["Minecraft Multi Launcher ran into an error"]
    assert "kaboom" in response["Result"][0]["SubTitle"]
