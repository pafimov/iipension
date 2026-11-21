"""Reference kernel for FR-2, not a portfolio engine. All inputs are scenario assumptions.

No network, ORM, framework, clock, LLM, float or tax defaults. Rounding policy v1:
retain Decimal precision during accumulation; round displayed balances half-up,
round minimum equal end-of-month contribution UP to kopeck. See ADR-002.
"""

from dataclasses import dataclass
from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal, localcontext

CENT = Decimal("0.01")
ZERO = Decimal("0")
ONE = Decimal("1")
CALCULATION_VERSION = "capital-reference-v1"


@dataclass(frozen=True)
class CapitalResult:
    available_capital: Decimal
    shortfall: Decimal
    required_monthly_contribution: Decimal | None


def _nonnegative(*values: Decimal) -> None:
    if any(not v.is_finite() or v < ZERO for v in values):
        raise ValueError("Amounts must be finite and nonnegative")


def required_reserve(target: Decimal, net_coupons: tuple[Decimal, ...]) -> Decimal:
    """FR-2.1: maximum positive prefix deficit; principal is deliberately absent."""
    _nonnegative(target, *net_coupons)
    if target == ZERO or not net_coupons:
        raise ValueError("A positive target and a nonempty horizon are required")
    deficit, reserve = ZERO, ZERO
    with localcontext() as ctx:
        ctx.prec = 50
        for coupon in net_coupons:
            deficit += target - coupon
            reserve = max(reserve, deficit)
        return reserve.quantize(CENT, rounding=ROUND_CEILING)


def capital_plan(
    *,
    required: Decimal,
    initial: Decimal,
    contribution: Decimal,
    months: int,
    monthly_rate: Decimal,
) -> CapitalResult:
    _nonnegative(required, initial, contribution)
    if not monthly_rate.is_finite() or monthly_rate <= -ONE:
        raise ValueError("Monthly rate must be finite and greater than -1")
    if isinstance(months, bool) or not isinstance(months, int) or not 0 <= months <= 1200:
        raise ValueError("Months must be an integer in [0, 1200]")
    with localcontext() as ctx:
        ctx.prec = 50
        factor = (ONE + monthly_rate) ** months
        annuity = sum(((ONE + monthly_rate) ** i for i in range(months)), ZERO)
        available = initial * factor + contribution * annuity
        minimum = (
            None
            if months == 0
            else (max(ZERO, (required - initial * factor) / annuity)).quantize(
                CENT, rounding=ROUND_CEILING
            )
        )
        return CapitalResult(
            available.quantize(CENT, rounding=ROUND_HALF_UP),
            max(ZERO, required - available).quantize(CENT, rounding=ROUND_HALF_UP),
            minimum,
        )
