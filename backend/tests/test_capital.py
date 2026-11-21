from decimal import Decimal as D

import pytest

from pension.domain.capital import capital_plan, required_reserve


def plan(required="120000", initial="0", contribution="8000", months=12, rate="0"):
    return capital_plan(
        required=D(required),
        initial=D(initial),
        contribution=D(contribution),
        months=months,
        monthly_rate=D(rate),
    )


def test_ac_fr_2_1_reserve_is_prefix_deficit_not_total_coupons():
    reserve = required_reserve(D("10000"), (D("0"), D("20000")))
    assert reserve == D("10000")
    assert D("110000") + reserve == D("120000")


def test_ac_fr_2_2_equal_contributions():
    result = plan()
    assert result.required_monthly_contribution == D("10000.00")
    assert result.available_capital == D("96000.00")
    assert result.shortfall == D("24000.00")


def test_ac_fr_2_4_end_of_month_contributions_and_upward_rounding():
    result = plan("1500", "1000", "100", 2, "0.01")
    assert result.available_capital == D("1221.10")
    assert result.shortfall == D("278.90")
    assert result.required_monthly_contribution == D("238.76")
    assert plan("1500", "1000", "238.76", 2, "0.01").shortfall == D("0")
    assert plan("1500", "1000", "238.75", 2, "0.01").shortfall > D("0")


def test_ac_fr_2_5_already_funded():
    assert plan(initial="120000", months=1).required_monthly_contribution == D("0")
    assert plan(initial="120000", months=1).shortfall == D("0")


def test_ac_fr_2_6_immediate_start_no_monthly_contribution():
    result = plan(initial="90000", months=0)
    assert result.required_monthly_contribution is None
    assert result.shortfall == D("30000")


@pytest.mark.parametrize("rate", ["-1", "-1.01", "NaN", "Infinity"])
def test_reject_invalid_rates(rate):
    with pytest.raises(ValueError):
        plan(rate=rate)


@pytest.mark.parametrize("months", [-1, 1201, True, 1.5])
def test_reject_invalid_horizon(months):
    with pytest.raises(ValueError):
        plan(months=months)


@pytest.mark.parametrize("value", ["-1", "NaN", "Infinity"])
def test_reject_invalid_money(value):
    with pytest.raises(ValueError):
        plan(initial=value)


def test_negative_valid_rate_and_repeatability():
    result = plan("1500", "1000", "100", 2, "-0.01")
    assert result.available_capital == D("1179.10")
    assert result == plan("1500", "1000", "100", 2, "-0.01")


def test_reserve_zero_when_each_prefix_is_covered():
    assert required_reserve(D("10"), (D("20"), D("0"))) == D("0")


def test_empty_calendar_is_not_a_valid_snapshot():
    with pytest.raises(ValueError):
        required_reserve(D("10"), ())
