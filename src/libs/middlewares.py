from django.http import JsonResponse


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
