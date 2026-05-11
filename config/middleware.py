from django.http import JsonResponse

JSON_MAX = 512 * 1024        # 512 KB
MULTIPART_MAX = 7 * 1024 * 1024  # 7 MB


class RequestSizeLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = request.META.get("CONTENT_TYPE", "")
            content_length = int(request.META.get("CONTENT_LENGTH") or 0)
            if "multipart" in content_type:
                if content_length > MULTIPART_MAX:
                    return JsonResponse(
                        {"error": f"File too large. Maximum allowed size is 7 MB."},
                        status=413,
                    )
            else:
                if content_length > JSON_MAX:
                    return JsonResponse(
                        {"error": f"Request body too large. Maximum allowed size is 512 KB for JSON."},
                        status=413,
                    )
        return self.get_response(request)
