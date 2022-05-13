import os
import subprocess

def clear_screen() -> None:
    os.system('clear' if os.name == 'posix' else 'cls')

def exec_command(command: str) -> str:
    return subprocess.check_output(command, shell=True).decode('utf-8')