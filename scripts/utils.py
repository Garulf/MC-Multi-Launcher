from subprocess import Popen, PIPE
from threading import Thread
from typing import List
from pathlib import Path


def console_bell():
    """Print a bell character to the console"""
    print('\a')


# def run(cmd: List[any]):
#     proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
#     try:
#         while True:
#             out = proc.stdout.readline()
#             err = proc.stderr.readline()
#             if out == b'' and proc.poll() is not None:
#                 break
#             if out:
#                 print(out.decode().strip())
#             if err:
#                 print(err.decode().strip())
#         proc.wait()
#         if proc.returncode != 0:
#             raise RuntimeError(
#                 f"Command {' '.join(cmd)} failed with code {proc.returncode}")
#     except KeyboardInterrupt:
#         proc.kill()
#         proc.wait()

def run(cmd: List[any], cwd: str = Path.cwd()) -> None:
    process = Popen(cmd, stdout=PIPE, stderr=PIPE,
                    stdin=PIPE, cwd=cwd)

    def read_buffer(process):
        while True:
            data = process.stdout.readline().decode("utf-8")
            if not data:
                break
            print(data.strip())
            err = process.stderr.readline().decode("utf-8")
            if err:
                print(err.strip())
    _thread = Thread(target=read_buffer, args=(process,))
    _thread.start()
    _thread.join()
    out, err = process.communicate()
    print(out.decode().strip())
    print(err.decode().strip())


def transform_to_absolute_path(path: str) -> str:
    return Path(path).resolve()
