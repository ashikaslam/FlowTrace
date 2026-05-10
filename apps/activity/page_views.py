from django.shortcuts import render


def activity_timeline(request, workspace_slug):
    return render(request, "activity/timeline.html", {"workspace_slug": workspace_slug})
