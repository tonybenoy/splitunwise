from decimal import Decimal
from typing import List

from pydantic import BaseModel


class UserNew(BaseModel):
    name: str


class SplitNew(BaseModel):
    user_id: int
    amount: Decimal


class ExpenseNew(BaseModel):
    user_id: int
    amount: Decimal
    splits: List[SplitNew]


class PaymentNew(BaseModel):
    user_id: int
    paid_to: int
    amount: Decimal
