from django.shortcuts import render


def note_detail(request, workspace_slug, note_id):
    return render(request, "notes/detail.html", {
        "workspace_slug": workspace_slug,
        "note_id": note_id,
    })
