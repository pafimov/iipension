def no_store_api(get_response):
    def middleware(request):
        response = get_response(request)
        if request.path.startswith("/api/"):
            response["Cache-Control"] = "no-store, private"
        return response

    return middleware
