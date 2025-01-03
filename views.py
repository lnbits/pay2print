from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer

from .crud import get_printer

pay2print_ext_generic = APIRouter(tags=["pay2print"])


@pay2print_ext_generic.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    user: User = Depends(check_user_exists),
):
    return template_renderer(["pay2print/templates"]).TemplateResponse(
        request, "pay2print/index.html", {"user": user.json()}
    )


@pay2print_ext_generic.get("/public/{printer_id}", response_class=HTMLResponse)
async def public(printer_id: str, request: Request):
    printer = await get_printer(printer_id)
    if not printer:
        return template_renderer().TemplateResponse(
            request, "error.html", {"err": "Printer not found"}, HTTPStatus.NOT_FOUND
        )
    return template_renderer(["pay2print/templates"]).TemplateResponse(
        request,
        "pay2print/public.html",
        {
            "printer_id": printer_id,
            "amount": printer.amount,
            "printer_name": printer.name,
            "width": printer.width,
            "height": printer.height,
        },
    )


@pay2print_ext_generic.get("/photo/{printer_id}", response_class=HTMLResponse)
async def photo(printer_id: str, request: Request):
    printer = await get_printer(printer_id)
    if not printer:
        return template_renderer().TemplateResponse(
            request, "error.html", {"err": "Printer not found"}, HTTPStatus.NOT_FOUND
        )
    return template_renderer(["pay2print/templates"]).TemplateResponse(
        request,
        "pay2print/photo.html",
        {
            "printer_id": printer_id,
            "amount": printer.amount,
            "printer_name": printer.name,
            "width": printer.width,
            "height": printer.height,
        },
    )


@pay2print_ext_generic.get("/text/{printer_id}", response_class=HTMLResponse)
async def text(printer_id: str, request: Request):
    printer = await get_printer(printer_id)
    if not printer:
        return template_renderer().TemplateResponse(
            request, "error.html", {"err": "Printer not found"}, HTTPStatus.NOT_FOUND
        )
    return template_renderer(["pay2print/templates"]).TemplateResponse(
        request,
        "pay2print/text.html",
        {
            "printer_id": printer_id,
            "amount": printer.amount,
            "printer_name": printer.name,
        },
    )
