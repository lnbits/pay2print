from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from lnbits.core.crud import get_wallet
from lnbits.core.models import WalletTypeInfo
from lnbits.core.services import create_invoice
from lnbits.decorators import check_user_exists, require_admin_key, require_invoice_key

from .crud import (
    create_print,
    create_printer,
    delete_printer,
    get_print,
    get_printer,
    get_printers,
    get_prints,
    update_printer,
)
from .helpers import check_printer, print_file_path, safe_file_name
from .models import CreatePrinter, Print, Printer, UploadPayment
from .services import print_service

pay2print_ext_api = APIRouter(
    prefix="/api/v1",
    tags=["pay2print"],
)


async def _validate_input_wallet(user_id: str, wallet_id: str) -> None:
    wallet = await get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(HTTPStatus.BAD_REQUEST, "Wallet not found.")
    if wallet.user != user_id:
        raise HTTPException(HTTPStatus.BAD_REQUEST, "Wallet does not belong to user.")


@pay2print_ext_api.get("/printer")
async def api_get_printers(
    key_info: WalletTypeInfo = Depends(require_invoice_key),
) -> list[Printer]:
    return await get_printers(key_info.wallet.user)


@pay2print_ext_api.get("/printer/check/{printer_id}")
async def api_check_printer(
    printer_id: str,
    key_info: WalletTypeInfo = Depends(require_invoice_key),
) -> None:
    printer = await get_printer(printer_id)
    if not printer:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Printer not found.")
    if key_info.wallet.user != printer.user_id:
        raise HTTPException(HTTPStatus.FORBIDDEN, "Not your printer.")
    try:
        check_printer(printer.host, printer.name)
    except Exception as exc:
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc)) from exc


@pay2print_ext_api.post("/printer")
async def api_create_printer(
    data: CreatePrinter,
    key_info: WalletTypeInfo = Depends(require_admin_key),
) -> Printer:
    if data.wallet != key_info.wallet.id:
        await _validate_input_wallet(key_info.wallet.user, data.wallet)
    return await create_printer(key_info.wallet.user, data)


@pay2print_ext_api.post(
    "/upload/{printer_id}",
    description="Public upload endpoint, returns a payment request.",
)
async def api_upload_print(printer_id: str, file: UploadFile) -> UploadPayment:
    printer = await get_printer(printer_id)
    if not printer:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Printer not found.")
    if not file or not file.filename or not file.content_type:
        raise HTTPException(HTTPStatus.BAD_REQUEST, "No file uploaded.")
    upload_file_path = safe_file_name(file.filename)
    open(upload_file_path, "wb").write(await file.read())
    payment = await create_invoice(
        wallet_id=printer.wallet,
        amount=printer.amount,
        memo=f"Print payment for file: {file.filename}",
        extra={"tag": "pay2print"},
    )
    await create_print(payment.payment_hash, printer_id, upload_file_path.name)

    return UploadPayment(
        payment_hash=payment.payment_hash, payment_request=payment.bolt11
    )


@pay2print_ext_api.get("/file/{print_id}", dependencies=[Depends(check_user_exists)])
async def api_show_file(print_id: str) -> FileResponse:
    _print = await get_print(print_id)
    if not _print:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Print not found.")

    return FileResponse(print_file_path(_print.file), filename=_print.file)


@pay2print_ext_api.put("/printer/{printer_id}")
async def api_update_printer(
    printer_id: str,
    data: CreatePrinter,
    key_info: WalletTypeInfo = Depends(require_admin_key),
) -> Printer:
    if data.wallet != key_info.wallet.id:
        await _validate_input_wallet(key_info.wallet.user, data.wallet)

    printer = await get_printer(printer_id)
    if not printer:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Printer not found.")
    if key_info.wallet.user != printer.user_id:
        raise HTTPException(HTTPStatus.FORBIDDEN, "User not allowed to update printer.")

    printer.wallet = data.wallet
    printer.host = data.host
    if data.name:
        printer.name = data.name

    return await update_printer(printer)


@pay2print_ext_api.delete("/printer/{printer_id}")
async def api_delete_printer(
    printer_id: str,
    key_info: WalletTypeInfo = Depends(require_admin_key),
) -> None:
    printer = await get_printer(printer_id)
    if not printer:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Printer not found.")
    if key_info.wallet.user != printer.user_id:
        raise HTTPException(HTTPStatus.FORBIDDEN, "User not allowed to delete printer.")
    return await delete_printer(printer_id)


@pay2print_ext_api.get(
    "/print/{printer_id}", dependencies=[Depends(require_invoice_key)]
)
async def api_get_prints(printer_id: str) -> list[Print]:
    printer = await get_printer(printer_id)
    if not printer:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Printer not found.")
    return await get_prints(printer_id)


@pay2print_ext_api.get(
    "/print/print/{print_id}",
    description="Admin only, trigger a manual print.",
)
async def api_print(
    print_id: str, key_info: WalletTypeInfo = Depends(require_admin_key)
):
    _print = await get_print(print_id)
    if not _print:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Print not found.")
    printer = await get_printer(_print.printer)
    if not printer:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Printer not found.")
    if key_info.wallet.user != printer.user_id:
        raise HTTPException(HTTPStatus.FORBIDDEN, "Not your printer.")
    try:
        await print_service(_print, printer)
    except Exception as exc:
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc)) from exc
