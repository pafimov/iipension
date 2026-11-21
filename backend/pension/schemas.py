from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from django.utils import timezone
from ninja import Schema
from pydantic import ConfigDict, Field, field_validator

Money = Annotated[Decimal, Field(ge=0, max_digits=16, decimal_places=2)]


class GoalInput(Schema):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    monthly_income: Annotated[Decimal, Field(gt=0, max_digits=16, decimal_places=2)]
    money_basis: Literal["today", "future"]
    payout_start: date
    payout_months: Annotated[int, Field(strict=True, ge=1, le=1200)]
    initial_capital: Money
    monthly_contribution: Money
    risk_notes: Annotated[str, Field(min_length=1, max_length=1000)]

    @field_validator(
        "monthly_income",
        "initial_capital",
        "monthly_contribution",
        mode="before",
        json_schema_input_type=str,
    )
    @classmethod
    def money_is_string(cls, value):
        if not isinstance(value, str):
            raise ValueError("Передавайте денежные суммы десятичной строкой")
        return value

    @field_validator("payout_start")
    @classmethod
    def valid_start(cls, value: date) -> date:
        if value.day != 1 or value < timezone.now().date().replace(day=1):
            raise ValueError("Нужен первый день текущего или будущего месяца")
        return value


class GoalOutput(Schema):
    id: UUID
    monthly_income: str
    money_basis: str
    payout_start: date
    payout_months: int
    initial_capital: str
    monthly_contribution: str
    risk_notes: str
    confirmed_at: datetime | None
    created_at: datetime

    @staticmethod
    def resolve_monthly_income(obj):
        return f"{obj.monthly_income:.2f}"

    @staticmethod
    def resolve_initial_capital(obj):
        return f"{obj.initial_capital:.2f}"

    @staticmethod
    def resolve_monthly_contribution(obj):
        return f"{obj.monthly_contribution:.2f}"


class GoalPage(Schema):
    items: list[GoalOutput]
    has_more: bool


class Confirmation(Schema):
    model_config = ConfigDict(extra="forbid")
    confirmed: Literal[True]

    @field_validator("confirmed", mode="before")
    @classmethod
    def explicit_boolean(cls, value):
        if type(value) is not bool or value is not True:
            raise ValueError("Нужно явное подтверждение true")
        return value


class Error(Schema):
    message: str
