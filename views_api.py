from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from lnbits.core.crud import get_wallet
from lnbits.core.models import WalletTypeInfo
from lnbits.decorators import require_admin_key, require_invoice_key

from .crud import (
    create_printer,
    delete_printer,
    get_printer,
    get_printers,
    get_prints,
    update_printer,
)
from .models import CreatePrinter, Print, Printer

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


@pay2print_ext_api.post("/printer")
async def api_create_printer(
    data: CreatePrinter,
    key_info: WalletTypeInfo = Depends(require_admin_key),
) -> Printer:
    if data.wallet != key_info.wallet.id:
        await _validate_input_wallet(key_info.wallet.user, data.wallet)
    return await create_printer(key_info.wallet.user, data)


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
