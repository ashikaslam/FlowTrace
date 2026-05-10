from django.shortcuts import render


def task_list(request, workspace_slug):
    return render(request, "tasks/list.html", {"workspace_slug": workspace_slug})


def task_detail(request, workspace_slug, task_id):
    return render(request, "tasks/detail.html", {"workspace_slug": workspace_slug, "task_id": task_id})
