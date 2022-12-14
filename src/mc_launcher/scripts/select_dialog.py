import sys
import tkinter as tk
from tkinter import filedialog
from pathlib import Path


from flox import Settings


def main():
    print("Hello World")
    root = tk.Tk()
    root.withdraw()
    d = filedialog.askdirectory()
    d = Path(d)
    if d.exists() and d.is_dir():
        settings_path = sys.argv[1]
        settings = Settings(settings_path)
        settings['launcher_dir'] = str(d)


if __name__ == '__main__':
    main()
