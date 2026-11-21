from django.urls import path

from pension import auth, health
from pension.api import api

urlpatterns = [
    path("health/live", health.live),
    path("health/ready", health.ready),
    path("api/auth/session", auth.session),
    path("api/auth/login", auth.sign_in),
    path("api/auth/logout", auth.sign_out),
    path("api/v1/", api.urls),
]
