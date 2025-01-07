import asyncio

from fastapi import APIRouter
from loguru import logger

from .crud import db
from .helpers import print_file, setup_upload_folder
from .tasks import wait_for_paid_invoices
from .views import pay2print_ext_generic
from .views_api import pay2print_ext_api
from .views_lnurl import pay2print_lnurl_router

scheduled_tasks: list[asyncio.Task] = []

pay2print_ext: APIRouter = APIRouter(prefix="/pay2print", tags=["pay2print"])
pay2print_ext.include_router(pay2print_ext_generic)
pay2print_ext.include_router(pay2print_ext_api)
pay2print_ext.include_router(pay2print_lnurl_router)

pay2print_static_files = [
    {
        "path": "/pay2print/static",
        "name": "pay2print_static",
    }
]


def pay2print_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def pay2print_start():
    from lnbits.tasks import create_permanent_unique_task

    setup_upload_folder()
    task = create_permanent_unique_task("ext_pay2print", wait_for_paid_invoices)
    scheduled_tasks.append(task)


__all__ = [
    "db",
    "pay2print_ext",
    "pay2print_start",
    "pay2print_static_files",
    "pay2print_stop",
    "print_file",
]
