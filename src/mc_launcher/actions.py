from pathlib import Path
import sys
from subprocess import Popen, CREATE_NO_WINDOW

from flox import Flox


class Action:

    SCRIPT = None

    def __init__(self, plugin: Flox):
        self.plugin = plugin

    def __call__(self, *args, **kwargs):
        self.run(*args, **kwargs)
