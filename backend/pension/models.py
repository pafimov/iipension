import uuid

from django.conf import settings
from django.db import models


class Goal(models.Model):
    """Append-only drafts: edits create a new draft; confirmed inputs are immutable."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    monthly_income = models.DecimalField(max_digits=16, decimal_places=2)
    money_basis = models.CharField(
        max_length=16, choices=[("today", "Today"), ("future", "Future")]
    )
    payout_start = models.DateField()
    payout_months = models.PositiveIntegerField()
    initial_capital = models.DecimalField(max_digits=16, decimal_places=2)
    monthly_contribution = models.DecimalField(max_digits=16, decimal_places=2)
    risk_notes = models.CharField(max_length=1000)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(monthly_income__gt=0), name="goal_income_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(initial_capital__gte=0), name="goal_capital_nonnegative"
            ),
            models.CheckConstraint(
                condition=models.Q(monthly_contribution__gte=0),
                name="goal_contribution_nonnegative",
            ),
            models.CheckConstraint(
                condition=models.Q(payout_months__gt=0), name="goal_horizon_positive"
            ),
        ]
