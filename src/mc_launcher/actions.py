from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog
from subprocess import Popen, CREATE_NO_WINDOW

from flox import Flox
from mc_launcher.scripts import select_dialog


class Action:

    SCRIPT = None

    def __init__(self, plugin: Flox):
        self.plugin = plugin

    def __call__(self, *args, **kwargs):
        self.run(*args, **kwargs)





class OpenFileDialog(Action):

    def __init__(self, plugin: Flox):
        self.plugin = plugin

    def run(self, *args, **kwargs):
        exe = sys.executable
        root = Path(exe).parent
        script = Path(root, 'mc_launcher',
                      'scripts', 'select_dialog.py')
        self.plugin.logger.warning(f'Running {exe} {script}')
        cmd = [script]
        p = Popen(cmd, creationflags=CREATE_NO_WINDOW)


if __name__ == '__main__':
    op = OpenFileDialog(Flox())
    op.run()
