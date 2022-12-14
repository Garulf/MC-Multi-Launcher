from pathlib import Path
import sys

from utils import run
from config import load_config, DEFAULT_VIRTUAL_ENV, DEFAULT_REQUIREMENTS_FILE


if sys.platform == "win32":
    PIP_NAME = 'pip.exe'
    PYTHON_NAME = 'python.exe'
else:
    PIP_NAME = 'pip'
    PYTHON_NAME = 'python'


def python_path(virtual_env: str = DEFAULT_VIRTUAL_ENV) -> str:
    return str(Path().cwd().joinpath(virtual_env, 'Scripts', PYTHON_NAME))


def pip_path(virtual_env: str = DEFAULT_VIRTUAL_ENV) -> str:
    return str(Path().cwd().joinpath(virtual_env, 'Scripts', PIP_NAME))


def is_virtual_env(virtual_env: str = DEFAULT_VIRTUAL_ENV) -> bool:
    return Path().cwd().joinpath(virtual_env).exists()


def create_venv(virtual_env: str = DEFAULT_VIRTUAL_ENV) -> None:
    run([python_path(virtual_env), '-m', 'venv', virtual_env])


def install_requirements(requirements_file: str = DEFAULT_REQUIREMENTS_FILE, virtual_env: str = DEFAULT_VIRTUAL_ENV) -> None:
    print(f"Installing requirements from {requirements_file}")
    run([pip_path(virtual_env), 'install', '-U', '-r', requirements_file])


def main():
    config = load_config()
    if not is_virtual_env(config.virtual_env):
        create_venv(config.virtual_env)
    install_requirements(config.requirements, config.virtual_env)
    install_requirements(config.requirements_dev, config.virtual_env)


if __name__ == '__main__':
    main()
