from os import path
from pathlib import Path, PurePath
from subprocess import PIPE, Popen
from time import time

from lnbits.settings import settings
from loguru import logger

upload_dir = Path(settings.lnbits_data_folder, "uploads")


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


def check_printer(host: str, printer_name: str):
    try:
        lines = run_command(["lpstat", "-h", host, "-a"])
        logger.debug(f"lpstat -h {host} -a: {lines}")
        if printer_name not in "\n".join(lines):
            raise PrinterError(f"Printer {printer_name} not found")
    except Exception as e:
        raise PrinterError(f"Error checking default printer: {e}") from e


def print_file(host: str, printer_name, file_name: str):
    path = print_file_path(file_name)
    logger.debug(f"Printing {path} to {host} {printer_name}")
    run_command(["lp", "-h", host, "-d", printer_name, str(path)])


def run_command(command: list[str]) -> list[str]:
    """Run a command and return the output as list of lines."""
    stdout = Popen(command, stdout=PIPE).stdout
    if not stdout:
        return []
    out = stdout.read().decode()
    return out.splitlines()
