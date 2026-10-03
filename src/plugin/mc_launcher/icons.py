from pathlib import Path

STATIC_DIR = Path(__file__).resolve().parent / "static"

ICONS = {icon.stem: icon for icon in STATIC_DIR.glob("*.png")}

DEFAULT = ICONS["default"]
COBWEB = ICONS["cobweb"]
