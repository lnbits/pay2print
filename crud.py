from datetime import datetime, timezone
from typing import Optional

from lnbits.db import Connection, Database

from .models import CreatePrinter, Print, Printer

db = Database("ext_pay2print")


async def create_print(payment_hash: str, printer_id: str, file_name: str) -> Print:
    _print = Print(
        payment_hash=payment_hash,
        file=file_name,
        printer=printer_id,
    )
    await db.insert("pay2print.print", _print)
    return _print


async def update_print(_print: Print, conn: Optional[Connection] = None) -> Print:
    _print.updated_at = datetime.now(timezone.utc)
    await (conn or db).update(
        "pay2print.print", _print, "WHERE payment_hash = :payment_hash"
    )
    return _print


async def get_print(payment_hash: str) -> Optional[Print]:
    return await db.fetchone(
        "SELECT * FROM pay2print.print WHERE payment_hash = :payment_hash",
        {"payment_hash": payment_hash},
        Print,
    )


async def create_printer(user_id: str, data: CreatePrinter) -> Printer:
    printer = Printer(
        user_id=user_id,
        wallet=data.wallet,
        host=data.host,
        amount=data.amount,
        width=data.width,
        height=data.height,
        name=data.name or "My Printer",
    )
    await db.insert("pay2print.printer", printer)
    return printer


async def update_printer(printer: Printer) -> Printer:
    await db.update("pay2print.printer", printer)
    return printer


async def get_prints(printer_id: str) -> list[Print]:
    return await db.fetchall(
        """
        SELECT * FROM pay2print.print WHERE printer = :printer
        ORDER BY updated_at DESC
        """,
        {"printer": printer_id},
        model=Print,
    )


async def delete_print(print_id: str) -> None:
    await db.execute(
        "DELETE FROM pay2print.print WHERE id = :id",
        {"id": print_id},
    )


async def get_printer(printer_id: str) -> Optional[Printer]:
    return await db.fetchone(
        "SELECT * FROM pay2print.printer WHERE id = :id",
        {"id": printer_id},
        Printer,
    )


async def get_printers(user_id: str) -> list[Printer]:
    return await db.fetchall(
        """
        SELECT * FROM pay2print.printer WHERE user_id = :user_id
        ORDER BY created_at DESC
        """,
        {"user_id": user_id},
        model=Printer,
    )


async def delete_printer(print_id: str) -> None:
    await db.execute(
        "DELETE FROM pay2print.printer WHERE id = :id",
        {"id": print_id},
    )
