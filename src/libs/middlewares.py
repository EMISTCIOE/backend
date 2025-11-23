from django.http import HttpResponsePermanentRedirect, JsonResponse


class BlockPostmanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the 'postman-token' header is present in the request
        if "postman-token" in request.headers:
            return JsonResponse(
                {"error": "Requests from Postman are not allowed"},
                status=403,
            )

        # Continue processing the request if not from Postman
        return self.get_response(request)


class CSPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add CSP headers to API responses
        if request.path.startswith("/api/"):
            response[
                "Content-Security-Policy"
            ] = "default-src 'self' https://notices.tcioe.edu.np"

        return response


class CdnRedirectMiddleware:
    """
    Redirect direct requests to the CDN domain back to the primary site.
    """

    CDN_HOST = "cdn.tcioe.edu.np"
    TARGET_HOST = "https://tcioe.edu.np"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0].lower()
        path = request.path or "/"

        if host == self.CDN_HOST and path in {"", "/"}:
            redirect_url = f"{self.TARGET_HOST}{request.get_full_path()}"
            return HttpResponsePermanentRedirect(redirect_url)

        return self.get_response(request)
