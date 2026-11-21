from uuid import UUID

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import NinjaAPI, Query, Status
from ninja.security import django_auth

from pension.models import Goal
from pension.schemas import Confirmation, Error, GoalInput, GoalOutput, GoalPage

api = NinjaAPI(
    title="Personal Pension API", version="0.1.0", auth=django_auth, docs_url=None, openapi_url=None
)


@api.get("goals", response=GoalPage, operation_id="listGoals")
def list_goals(request, offset: int = Query(0, ge=0, le=100_000)):
    rows = list(Goal.objects.filter(owner=request.user)[offset : offset + 51])
    return {"items": rows[:50], "has_more": len(rows) > 50}


@api.post("goals", response={201: GoalOutput}, operation_id="createGoal")
def create_goal(request, payload: GoalInput):
    goal = Goal.objects.create(owner=request.user, **payload.model_dump())
    return Status(201, goal)


@api.post(
    "goals/{goal_id}/confirm",
    response={200: GoalOutput, 409: Error},
    operation_id="confirmGoal",
)
@transaction.atomic
def confirm_goal(request, goal_id: UUID, payload: Confirmation):
    goal = get_object_or_404(Goal.objects.select_for_update(), id=goal_id, owner=request.user)
    if goal.payout_start < timezone.now().date().replace(day=1):
        return Status(409, {"message": "Дата цели устарела. Создайте новый черновик."})
    if goal.confirmed_at is None:
        goal.confirmed_at = timezone.now()
        goal.save(update_fields=["confirmed_at"])
    return goal
