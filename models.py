from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from lnbits.core.models import PaymentState
from lnbits.helpers import urlsafe_short_hash
from pydantic import BaseModel, Field


class PrintStatus(str, Enum):
    WAITING = "waiting"
    PRINTING = "printing"
    SUCCESS = "success"
    FAILED = "failed"

    def __str__(self) -> str:
        return self.value


class Printer(BaseModel):
    id: str = Field(default_factory=urlsafe_short_hash)
    user_id: str
    wallet: str
    host: str
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CreatePrinter(BaseModel):
    wallet: str
    host: str
    name: Optional[str] = None


class Print(BaseModel):
    id: str = Field(default_factory=urlsafe_short_hash)
    printer: str
    payment_hash: str
    file: str
    payment_status: PaymentState = PaymentState.PENDING
    print_status: PrintStatus = PrintStatus.WAITING
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CreatePrint(BaseModel):
    file: str
    printer: str
