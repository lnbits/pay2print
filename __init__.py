import asyncio

from fastapi import APIRouter
from lnbits.db import Database
from loguru import logger

from .tasks import wait_for_paid_invoices
from .views import pay2print_ext_generic
from .views_api import pay2print_ext_api

db = Database("ext_pay2print")

scheduled_tasks: list[asyncio.Task] = []

pay2print_ext: APIRouter = APIRouter(prefix="/pay2print", tags=["pay2print"])
pay2print_ext.include_router(pay2print_ext_generic)
pay2print_ext.include_router(pay2print_ext_api)

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

    task = create_permanent_unique_task("ext_testing", wait_for_paid_invoices)
    scheduled_tasks.append(task)
