from mc_launcher import config


def write(tmp_path, text, encoding="utf-8"):
    path = tmp_path / "launcher.cfg"
    path.write_bytes(text.encode(encoding))
    return path


def test_reads_key_value_pairs(tmp_path):
    path = write(tmp_path, "InstanceDir=instances\nIconsDir=icons\n")
    assert config.load(path) == {"InstanceDir": "instances", "IconsDir": "icons"}


def test_skips_sections_comments_and_lines_without_equals(tmp_path):
    path = write(tmp_path, "[General]\n# comment\n; other comment\n\nJunk line\nname=Base\n")
    assert config.load(path) == {"name": "Base"}


def test_value_keeps_extra_equals_signs(tmp_path):
    path = write(tmp_path, "name=Survival=Hardcore\n")
    assert config.load(path)["name"] == "Survival=Hardcore"


def test_strips_qsettings_quotes_and_escapes(tmp_path):
    path = write(tmp_path, 'name="Create, Above and Beyond"\nInstanceDir=D:\\\\Games\\\\instances\n')
    props = config.load(path)
    assert props["name"] == "Create, Above and Beyond"
    assert props["InstanceDir"] == "D:\\Games\\instances"


def test_decodes_qt_unicode_escapes(tmp_path):
    path = write(tmp_path, "name=\\x4e2d\\x6587\n")
    assert config.load(path)["name"] == "中文"


def test_reads_utf8_with_bom(tmp_path):
    path = write(tmp_path, "name=Base\n", encoding="utf-8-sig")
    assert config.load(path) == {"name": "Base"}


def test_non_utf8_file_does_not_raise(tmp_path):
    path = write(tmp_path, "name=中文实例\nInstanceDir=instances\n", encoding="gbk")
    props = config.load(path)
    assert props["InstanceDir"] == "instances"
    assert "name" in props
