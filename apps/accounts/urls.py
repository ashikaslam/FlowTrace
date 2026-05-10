from django.urls import path
from . import page_views

urlpatterns = [
    path("", page_views.landing, name="landing"),
    path("register/", page_views.register_page, name="register"),
    path("workspace/<str:workspace_slug>/login/", page_views.workspace_login_page, name="workspace-login"),
    path("logout/", page_views.logout_page, name="logout"),
]
