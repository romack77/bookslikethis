from django import http
from django import test as dj_test
from django.test import client

from core import middleware
from core import test


class IPWhitelistMiddlewareTest(test.TestCase):

    def setUp(self):
        self.request_ip = '1.1.1.1'
        self.request = client.RequestFactory().get(
            '/', REMOTE_ADDR=self.request_ip)
        self.default_response = http.HttpResponse('default')
        self.middle_inst = middleware.IPWhitelistMiddleware(
            lambda r: self.default_response)

    def test_allowed(self):
        with dj_test.override_settings(
                IP_WHITELIST='%s,1.2.3.4' % self.request_ip):
            response = self.middle_inst(self.request)
        self.assertEqual(response.status_code, 200)

    def test_not_allowed(self):
        request = client.RequestFactory().get(
            '/', REMOTE_ADDR='2.2.2.2')
        with dj_test.override_settings(IP_WHITELIST='1.1.1.1,1.2.3.4'):
            response = self.middle_inst(request)
        self.assertEqual(response.status_code, 403)

    def test_no_whitelist(self):
        response = self.middle_inst(self.request)
        self.assertEqual(response.status_code, 200)

    def test_list_whitelist(self):
        with dj_test.override_settings(
                IP_WHITELIST=[self.request_ip, '1.2.3.4']):
            response = self.middle_inst(self.request)
        self.assertEqual(response.status_code, 200)

    def test_http_x_forwarded_for(self):
        """This header takes precedence over REMOTE_ADDR."""
        good_ip = '1.1.1.1'
        request = client.RequestFactory().get(
            '/', HTTP_X_FORWARDED_FOR=good_ip, REMOTE_ADDR='2.2.2.2')
        with dj_test.override_settings(IP_WHITELIST=good_ip):
            response = self.middle_inst(request)
        self.assertEqual(response.status_code, 200)

        request = client.RequestFactory().get(
            '/', HTTP_X_FORWARDED_FOR='2.2.2.2', REMOTE_ADDR=good_ip)
        with dj_test.override_settings(IP_WHITELIST=good_ip):
            response = self.middle_inst(request)
        self.assertEqual(response.status_code, 403)

    def test_multi_http_x_forwarded_for(self):
        """Use the first forwarded ip."""
        good_ip = '1.1.1.1'
        request = client.RequestFactory().get(
            '/',
            HTTP_X_FORWARDED_FOR='%s,1.2.3.4' % good_ip,
            REMOTE_ADDR='2.2.2.2')
        with dj_test.override_settings(IP_WHITELIST=good_ip):
            response = self.middle_inst(request)
        self.assertEqual(response.status_code, 200)


class JsonDebugToolbarMiddlewareTest(test.TestCase):

    def setUp(self):
        self.request = client.RequestFactory().get(
            '/?%s' % middleware.JsonDebugToolbarMiddleware.TOOLBAR_PARAM)
        self.json_response = http.HttpResponse(
            '{"ok": true}', content_type='application/json')

    def test_no_debug_param(self):
        """Responses are not modified without the debug toolbar param."""
        request = client.RequestFactory().get('/')
        middle_inst = middleware.JsonDebugToolbarMiddleware(
            lambda r: self.json_response)
        final_response = middle_inst(request)
        self.assertEqual(final_response.content, self.json_response.content)

    def test_json_content(self):
        """JSON responses are wrapped in HTML."""
        middle_inst = middleware.JsonDebugToolbarMiddleware(
            lambda r: self.json_response)
        final_response = middle_inst(self.request)
        self.assertTrue(
            final_response.content.startswith('<html>'.encode('utf-8')))
        self.assertIn('"ok": true'.encode('utf-8'), final_response.content)

    def test_bad_json_content(self):
        """Invalid JSON responses are not modified."""
        response = http.HttpResponse(
            '{broken', content_type='application/json')
        middle_inst = middleware.JsonDebugToolbarMiddleware(
            lambda r: response)
        final_response = middle_inst(self.request)
        self.assertEqual(final_response.content, response.content)

    def test_binary_content(self):
        """Binary responses are wrapped in HTML."""
        response = http.HttpResponse(
            'binary', content_type='application/octet-stream')
        middle_inst = middleware.JsonDebugToolbarMiddleware(
            lambda r: response)
        final_response = middle_inst(self.request)
        self.assertTrue(final_response.content.startswith(
            '<html><body>Binary Data'.encode('utf-8')))

    def test_html_content(self):
        """HTML responses are not modified."""
        response = http.HttpResponse(
            '<html></html>', content_type='text/html')
        middle_inst = middleware.JsonDebugToolbarMiddleware(
            lambda r: response)
        final_response = middle_inst(self.request)
        self.assertEqual(final_response.content, response.content)
