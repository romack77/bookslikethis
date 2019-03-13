from debug_toolbar import middleware


def show_toolbar(request):
    """Determines whether debug toolbar should be shown for the request.

    Requires settings.DEBUG=True, 'debug_toolbar' GET param present,
    and request ip in settings.INTERNAL_IPS.

    Args:
        request: HttpRequest object.

    Returns:
        Boolean.
    """
    if ('debug_toolbar' not in request.GET and
            '/__debug__/' not in request.path):
        return False
    return middleware.show_toolbar(request)
