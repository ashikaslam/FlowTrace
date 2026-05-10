from django.shortcuts import render, redirect


def landing(request):
    return render(request, "accounts/landing.html")


def register_page(request):
    return render(request, "accounts/register.html")


def workspace_login_page(request, workspace_slug):
    return render(request, "accounts/login.html", {"workspace_slug": workspace_slug})


def logout_page(request):
    response = redirect("landing")
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response
