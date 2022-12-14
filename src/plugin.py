import sys
import os


plugin_root = sys.argv[0]
os.chdir(os.path.dirname(os.path.abspath(plugin_root)))


from mc_launcher import plugin

if __name__ == "__main__":
    plugin.run()
