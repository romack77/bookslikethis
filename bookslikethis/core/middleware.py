import json
import logging

from django import http
from django.conf import settings

log = logging.getLogger(__name__)


class IPWhitelistMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not self._is_allowed(request):
            return http.HttpResponseForbidden()
        return self.get_response(request)

    def _is_allowed(self, request):
        ip = IPWhitelistMiddleware._get_client_ip(request)
        whitelist = settings.IP_WHITELIST
        if whitelist is not None and type(whitelist) in (list, str):
            if type(whitelist) == str:
                whitelist = whitelist.split(',')
            if ip not in whitelist:
                return False
        return True

    @staticmethod
    def _get_client_ip(request):
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip:
            return ip.split(',')[0]
        return request.META.get('REMOTE_ADDR') or ''

    def process_exception(self, request, exception):
        return None


class JsonDebugToolbarMiddleware(object):
    """Converts JSON responses to HTML for the Django Debug Toolbar.

    Responses are converted if the ?debug_toolbar GET parameter is present.
    Based on https://stackoverflow.com/a/19249559.
    """

    TOOLBAR_PARAM = 'debug_toolbar'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if JsonDebugToolbarMiddleware.TOOLBAR_PARAM in request.GET:
            if 'application/octet-stream' in response['Content-Type']:
                new_content = (
                    '<html><body>Binary Data, '
                    'Length: %s</body></html>' % len(response.content))
                response = http.HttpResponse(new_content)
            elif 'text/html' not in response['Content-Type']:
                content = response.content
                try:
                    json_ = json.loads(content)
                    content = json.dumps(json_, sort_keys=True, indent=2)
                except ValueError:
                    pass
                else:
                    response = http.HttpResponse(
                        '<html><body><pre>%s</pre></body></html>' % content)

        return response

    def process_exception(self, request, exception):
        return None
