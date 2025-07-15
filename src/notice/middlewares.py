# custom_middleware.py


class CSPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add CSP headers to API responses
        if request.path.startswith("/api/"):
            response[
                "Content-Security-Policy"
            ] = "default-src 'self' https://notices.tcioe.edu.np https://docs.google.com https://google.com"
            # Add other CSP directives as needed for your API responses

        return response
