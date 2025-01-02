import asyncio

from lnbits.core.models import Payment, PaymentState
from lnbits.tasks import register_invoice_listener
from loguru import logger

from .crud import get_print, get_printer, update_print
from .services import print_service


async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, "ext_pay2print")

    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


async def on_invoice_paid(payment: Payment) -> None:
    if payment.extra.get("tag") == "pay2print":
        logger.info("pay2print extension received payment")
        _print = await get_print(payment.payment_hash)
        assert _print, "Print not found."
        printer = await get_printer(_print.printer)
        assert printer, "Printer not found."
        _print.payment_status = PaymentState.SUCCESS
        await update_print(_print)
        try:
            await print_service(_print, printer)
        except Exception as exc:
            logger.error(f"Error printing {_print.id}: {exc}")
