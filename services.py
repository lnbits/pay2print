import asyncio

from .crud import db, update_print
from .helpers import check_printer, print_file
from .models import Print, Printer, PrintStatus


async def print_service(_print: Print, printer: Printer) -> None:
    check_printer(printer.host, printer.name)
    async with db.connect() as conn:
        _print.print_status = PrintStatus.PRINTING
        await update_print(_print, conn=conn)
        try:
            print_file(printer.host, printer.name, _print.file)
            await asyncio.sleep(5)  # simulate printing time
            _print.print_status = PrintStatus.SUCCESS
            await update_print(_print, conn=conn)
            return
        except Exception as exc:
            _print.print_status = PrintStatus.FAILED
            await update_print(_print, conn=conn)
            raise exc
