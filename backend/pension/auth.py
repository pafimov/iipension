import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST


def csrf_failure(request, reason=""):
    return JsonResponse(
        {"message": "Сессия устарела. Обновите страницу и повторите действие."}, status=403
    )


def locked_out(request, credentials=None, *args, **kwargs):
    return JsonResponse({"message": "Слишком много попыток. Повторите вход позже."}, status=429)


@require_GET
@never_cache
@ensure_csrf_cookie
def session(request):
    user = {"username": request.user.get_username()} if request.user.is_authenticated else None
    return JsonResponse({"user": user})


@require_POST
@never_cache
def sign_in(request):
    # This ordinary Django view is protected by CsrfViewMiddleware BEFORE authentication.
    try:
        data = json.loads(request.body)
        username, password = data["username"], data["password"]
        if not isinstance(username, str) or not isinstance(password, str):
            raise ValueError
        if not username or len(username) > 150 or not password or len(password) > 1024:
            raise ValueError
    except (ValueError, KeyError, TypeError):
        return JsonResponse({"message": "Проверьте имя пользователя и пароль."}, status=400)
    user = authenticate(request=request, username=username, password=password)
    if user is None:
        return JsonResponse({"message": "Не удалось войти. Проверьте данные."}, status=401)
    login(request, user)
    return JsonResponse({"user": {"username": user.get_username()}})


@require_POST
@never_cache
def sign_out(request):
    logout(request)
    return JsonResponse({"user": None})
