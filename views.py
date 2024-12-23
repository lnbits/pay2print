from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer

pay2print_ext_generic = APIRouter(tags=["pay2print"])


@pay2print_ext_generic.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    user: User = Depends(check_user_exists),
):
    return template_renderer(["pay2print/templates"]).TemplateResponse(
        request, "index.html", {"user": user.json()}
    )
