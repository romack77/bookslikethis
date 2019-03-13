from unittest import mock

from debug_toolbar import middleware
from django.test import client

from core import debug
from core import test


class ShowToolbarTest(test.TestCase):

    def test_toolbar_param(self):
        request = client.RequestFactory().get('/?debug_toolbar')
        with mock.patch.object(
                middleware, 'show_toolbar', return_value=True) as show_mock:
            self.assertTrue(debug.show_toolbar(request))
            show_mock.return_value = False
            self.assertFalse(debug.show_toolbar(request))

    def test_toolbar_path(self):
        request = client.RequestFactory().get('/__debug__/stuff')
        with mock.patch.object(
                middleware, 'show_toolbar', return_value=True) as show_mock:
            self.assertTrue(debug.show_toolbar(request))
            show_mock.return_value = False
            self.assertFalse(debug.show_toolbar(request))

    def test_bad_request(self):
        request = client.RequestFactory().get('/bad/?bad')
        with mock.patch.object(
                middleware, 'show_toolbar', return_value=True) as show_mock:
            self.assertFalse(debug.show_toolbar(request))
            show_mock.return_value = False
            self.assertFalse(debug.show_toolbar(request))

