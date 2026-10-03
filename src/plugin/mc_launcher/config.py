import locale
import re
from pathlib import Path
from typing import Dict, Union

_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"', "#": "#", ";": ";", "0": "\0"}
_ESCAPE_PATTERN = re.compile(r"\\(x[0-9a-fA-F]{1,4}|.)")


def load(path: Union[str, Path]) -> Dict[str, str]:
    """Parse a MultiMC, PolyMC or Prism Launcher .cfg file into a flat dict."""
    props = {}
    for line in _read_text(Path(path)).splitlines():
        line = line.strip()
        if not line or line[0] in "#;[" or "=" not in line:
            continue
        key, value = line.split("=", 1)
        props[key.strip()] = _parse_value(value.strip())
    return props


def _read_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", locale.getpreferredencoding(False)):
        try:
            return data.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return data.decode("utf-8", errors="replace")


def _parse_value(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1]
    return _ESCAPE_PATTERN.sub(_unescape, value)


def _unescape(match: "re.Match[str]") -> str:
    token = match.group(1)
    if token[0] == "x" and len(token) > 1:
        return chr(int(token[1:], 16))
    return _ESCAPES.get(token, match.group(0))
