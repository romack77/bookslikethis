import logging
from unittest import mock

from django import test
from webpack_loader import loader


class TestCase(test.TestCase):
    """Base test case for this project."""

    # Disables caching to avoid test pollution.
    MOCK_CACHE = True

    def _setUp(self):
        # Don't truncate assertion diffs by default.
        self.maxDiff = None
        # Suppress log messages below error.
        logging.disable(logging.ERROR)

    def run(self, *args, **kwargs):
        self._setUp()
        # Don't load or rely on compiled static files.
        with mock.patch.object(loader.WebpackLoader, 'get_bundle'):
            if self.MOCK_CACHE:
                with self.settings(CACHE_ENABLED=False):
                    super().run(*args, **kwargs)
            else:
                super().run(*args, **kwargs)
