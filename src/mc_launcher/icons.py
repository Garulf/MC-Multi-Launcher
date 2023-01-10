import sys
from pathlib import Path

STATIC_DIR = Path(sys.argv[0]).parent.joinpath('mc_launcher', 'static')

CHICKEN = STATIC_DIR.joinpath('chicken.png')
CREEPER = STATIC_DIR.joinpath('creeper.png')
DEFAULT = STATIC_DIR.joinpath('default.png')
ENDERPEARL = STATIC_DIR.joinpath('enderpearl.png')
FLAME = STATIC_DIR.joinpath('flame.png')
FTB_GLOW = STATIC_DIR.joinpath('ftb_glow.png')
FTB_LOGO = STATIC_DIR.joinpath('ftb_logo.png')
GEAR = STATIC_DIR.joinpath('gear.png')
HEROBRINE = STATIC_DIR.joinpath('herobrine.png')
INFINITY = STATIC_DIR.joinpath('infinity.png')
MAGITECH = STATIC_DIR.joinpath('magitech.png')
MEAT = STATIC_DIR.joinpath('meat.png')
NETHERSTAR = STATIC_DIR.joinpath('netherstar.png')
SKELETON = STATIC_DIR.joinpath('skeleton.png')
SQUARECREEPER = STATIC_DIR.joinpath('squarecreeper.png')
STEVE = STATIC_DIR.joinpath('steve.png')
COBWEB = STATIC_DIR.joinpath('cobweb.png')

ICONS = {
    'chicken': CHICKEN,
    'creeper': CREEPER,
    'default': DEFAULT,
    'enderpearl': ENDERPEARL,
    'flame': FLAME,
    'ftb_glow': FTB_GLOW,
    'ftb_logo': FTB_LOGO,
    'gear': GEAR,
    'herobrine': HEROBRINE,
    'infinity': INFINITY,
    'magitech': MAGITECH,
    'meat': MEAT,
    'netherstar': NETHERSTAR,
    'skeleton': SKELETON,
    'squarecreeper': SQUARECREEPER,
    'steve': STEVE,
    'cobweb': COBWEB,
}
