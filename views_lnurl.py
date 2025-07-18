import json
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Query, Request
from lnbits.core.services import create_invoice
from lnurl import (
    CallbackUrl,
    LightningInvoice,
    LnurlPayActionResponse,
    LnurlPayMetadata,
    LnurlPayResponse,
    Max144Str,
    MessageAction,
    MilliSatoshi,
)
from pydantic import parse_obj_as

from .crud import (
    create_print,
    get_printer,
)

pay2print_lnurl_router = APIRouter()


@pay2print_lnurl_router.get(
    "/api/v1/lnurl/{printer_id}",
    status_code=HTTPStatus.OK,
    name="pay2print.api_lnurl_response",
)
async def api_lnurl_response(request: Request, printer_id: str) -> LnurlPayResponse:
    printer = await get_printer(printer_id)
    if not printer:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Printer does not exist."
        )
    url = request.url_for("pay2print.api_lnurl_callback", printer_id=printer_id)
    callback_url = parse_obj_as(CallbackUrl, str(url))

    return LnurlPayResponse(
        callback=callback_url,
        minSendable=MilliSatoshi(printer.amount * 1000),
        maxSendable=MilliSatoshi(printer.amount * 1000),
        metadata=LnurlPayMetadata(
            json.dumps([["text/plain", f"Pay to print {printer.name}"]])
        ),
        # TODO remove after lnurl lib update
        commentAllowed=None,
        payerData=None,
        allowsNostr=None,
        nostrPubkey=None,
    )


@pay2print_lnurl_router.get(
    "/api/v1/lnurl/cb/{printer_id}",
    status_code=HTTPStatus.OK,
    name="pay2print.api_lnurl_callback",
)
async def api_lnurl_callback(
    printer_id: str,
    amount: int = Query(...),
) -> LnurlPayActionResponse:
    printer = await get_printer(printer_id)
    if not printer:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Printer does not exist."
        )
    if amount != printer.amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Amount must be {printer.amount}.",
        )
    payment = await create_invoice(
        wallet_id=printer.wallet,
        amount=printer.amount,
        memo=f"Pay to print {printer.name}",
        extra={"tag": "pay2print"},
    )
    await create_print(printer_id, payment.payment_hash, "lnurl.txt")
    message = parse_obj_as(Max144Str, "Printing! Thank you")
    action = MessageAction(message=message)
    invoice = parse_obj_as(LightningInvoice, LightningInvoice(payment.bolt11))
    return LnurlPayActionResponse(pr=invoice, successAction=action, routes=[])
