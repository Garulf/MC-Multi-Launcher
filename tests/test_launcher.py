from pathlib import Path

import pytest

from mc_launcher import launcher
from mc_launcher.launcher import MCLauncher, detect_launchers, launcher_from_path

WINDOWS_ENV = ("LOCALAPPDATA", "APPDATA", "PROGRAMFILES", "PROGRAMFILES(X86)", "USERPROFILE")


@pytest.fixture(autouse=True)
def clean_env(monkeypatch, tmp_path):
    for var in WINDOWS_ENV:
        monkeypatch.delenv(var, raising=False)
    roaming = tmp_path / "Roaming"
    roaming.mkdir()
    monkeypatch.setenv("APPDATA", str(roaming))
    return roaming


def make_install(root: Path, exe="prismlauncher.exe") -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / exe).write_bytes(b"MZ")
    return root


def make_instance(instances: Path, folder: str, name: str) -> None:
    (instances / folder).mkdir(parents=True)
    (instances / folder / "instance.cfg").write_text(f"name={name}\n", encoding="utf-8")


def test_portable_install_keeps_data_beside_exe(tmp_path):
    root = make_install(tmp_path / "Games" / "MultiMC", exe="MultiMC.exe")
    (root / "multimc.cfg").write_text("InstanceDir=instances\n", encoding="utf-8")
    make_instance(root / "instances", "base", "Base")

    mc = launcher_from_path(root)

    assert mc.name == "MultiMC"
    assert mc.data_dir == root
    assert [i.name for i in mc.instances()] == ["Base"]


def test_multimc_without_cfg_is_portable(tmp_path):
    root = make_install(tmp_path / "MultiMC", exe="MultiMC.exe")
    assert launcher_from_path(root).instance_dir == root / "instances"


def test_installed_prism_reads_data_from_appdata(tmp_path, clean_env):
    root = make_install(tmp_path / "Local" / "Programs" / "PrismLauncher")
    data = clean_env / "PrismLauncher"
    data.mkdir()
    (data / "prismlauncher.cfg").write_text("[General]\nInstanceDir=instances\n", encoding="utf-8")
    make_instance(data / "instances", "pack", "Pack")

    mc = launcher_from_path(root)

    assert mc.name == "Prism Launcher"
    assert mc.data_dir == data
    assert [i.id for i in mc.instances()] == ["pack"]


def test_portable_marker_wins_over_appdata(tmp_path, clean_env):
    root = make_install(tmp_path / "Prism")
    (root / "portable.txt").write_text("", encoding="utf-8")
    (clean_env / "PrismLauncher").mkdir()
    assert launcher_from_path(root).data_dir == root


def test_relative_custom_instance_dir_resolves_against_data_dir(tmp_path):
    root = make_install(tmp_path / "MultiMC", exe="multimc.exe")
    (root / "multimc.cfg").write_text("InstanceDir=my_instances\n", encoding="utf-8")
    assert launcher_from_path(root).instance_dir == root / "my_instances"


def test_absolute_instance_dir_is_used_as_is(tmp_path):
    root = make_install(tmp_path / "MultiMC", exe="multimc.exe")
    elsewhere = tmp_path / "elsewhere"
    escaped = str(elsewhere).replace("\\", "\\\\")
    (root / "multimc.cfg").write_text(f"InstanceDir={escaped}\n", encoding="utf-8")
    assert launcher_from_path(root).instance_dir == elsewhere


def test_accepts_path_to_the_exe(tmp_path):
    root = make_install(tmp_path / "MultiMC", exe="MultiMC.exe")
    mc = launcher_from_path(root / "MultiMC.exe")
    assert mc is not None
    assert mc.install_dir == root


def test_accepts_quoted_path(tmp_path):
    root = make_install(tmp_path / "MultiMC", exe="MultiMC.exe")
    assert launcher_from_path(f'"{root}"') is not None


@pytest.mark.parametrize("value", ["", "   ", "Z:/does/not/exist"])
def test_invalid_paths_return_none(value):
    assert launcher_from_path(value) is None


def test_folder_without_launcher_returns_none(tmp_path):
    assert launcher_from_path(tmp_path) is None


def test_instances_skip_folders_without_config(tmp_path):
    root = make_install(tmp_path / "MultiMC", exe="MultiMC.exe")
    make_instance(root / "instances", "base", "Base")
    (root / "instances" / "_MMC_TEMP").mkdir()
    (root / "instances" / "instgroups.json").write_text("{}", encoding="utf-8")
    assert [i.id for i in launcher_from_path(root).instances()] == ["base"]


def test_missing_instance_dir_means_no_instances(tmp_path):
    root = make_install(tmp_path / "MultiMC", exe="MultiMC.exe")
    assert launcher_from_path(root).instances() == []


def test_detects_launchers_in_known_locations(tmp_path, monkeypatch):
    local = tmp_path / "Local"
    make_install(local / "Programs" / "PrismLauncher")
    make_install(tmp_path / "Program Files" / "PolyMC", exe="polymc.exe")
    make_install(tmp_path / "User" / "scoop" / "apps" / "multimc" / "current", exe="MultiMC.exe")
    monkeypatch.setenv("LOCALAPPDATA", str(local))
    monkeypatch.setenv("PROGRAMFILES", str(tmp_path / "Program Files"))
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "User"))

    names = sorted(mc.name for mc in detect_launchers())

    assert names == ["MultiMC", "PolyMC", "Prism Launcher"]


def test_detect_ignores_duplicate_locations(tmp_path, monkeypatch):
    make_install(tmp_path / "PrismLauncher")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setenv("PROGRAMFILES", str(tmp_path))
    assert len(detect_launchers()) == 1


def test_detect_without_windows_env_finds_nothing(monkeypatch):
    for var in WINDOWS_ENV:
        monkeypatch.delenv(var, raising=False)
    assert detect_launchers() == []


def test_launch_runs_exe_with_instance_id(tmp_path, monkeypatch):
    root = make_install(tmp_path / "MultiMC", exe="MultiMC.exe")
    calls = []
    monkeypatch.setattr(launcher, "Popen", lambda cmd, cwd, **streams: calls.append((cmd, cwd, streams)))

    launcher_from_path(root).launch("my pack")

    devnull = {"stdin": launcher.DEVNULL, "stdout": launcher.DEVNULL, "stderr": launcher.DEVNULL}
    assert calls == [([str(root / "MultiMC.exe"), "--launch", "my pack"], root, devnull)]


def test_equality_is_by_executable(tmp_path):
    root = make_install(tmp_path / "MultiMC", exe="MultiMC.exe")
    assert MCLauncher(root / "MultiMC.exe") == launcher_from_path(root)
