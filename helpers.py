from os import path
from pathlib import Path, PurePath
from subprocess import PIPE, Popen
from time import time

from lnbits.settings import settings
from loguru import logger

upload_dir = Path(settings.lnbits_data_folder, "uploads")

cmd_check_default_printer = ["lpstat", "-d"]
cmd_print = "lpr"


class PrinterError(Exception):
    """Error is thrown we we cannot connect to the printer."""


def setup_upload_folder():
    upload_dir.mkdir(parents=True, exist_ok=True)


def safe_file_name(file_name: str) -> Path:
    # strip leading path from file name to avoid directory traversal attacks
    safe_name = PurePath(file_name).name
    if path.exists(safe_name):
        safe_name = f"{int(time())}_{safe_name}"
    return Path(upload_dir, file_name)


def print_file_path(file_name: str) -> Path:
    return Path(upload_dir, file_name)


def check_printer():
    try:
        lines = run_command(cmd_check_default_printer)
        if len(lines) == 0:
            raise PrinterError("No default printer found")
        logger.debug(f"Default printer: {lines[0]}")
    except Exception as e:
        raise PrinterError(f"Error checking default printer: {e}") from e


def print_file(file_name: str):
    path = print_file_path(file_name)
    run_command([cmd_print, str(path)])


def run_command(command: list[str]) -> list[str]:
    """Run a command and return the output as list of lines."""
    stdout = Popen(command, stdout=PIPE).stdout
    if not stdout:
        return []
    out = stdout.read().decode()
    return out.splitlines()
