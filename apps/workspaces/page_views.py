from django.shortcuts import render


def manager_dashboard(request, workspace_slug):
    return render(request, "dashboard/manager.html", {"workspace_slug": workspace_slug})


def developer_dashboard(request, workspace_slug):
    return render(request, "dashboard/developer.html", {"workspace_slug": workspace_slug})


def workspace_settings(request, workspace_slug):
    return render(request, "dashboard/settings.html", {"workspace_slug": workspace_slug})
