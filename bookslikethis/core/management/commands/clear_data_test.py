from unittest import mock

from core import factories
from core import test
from core.management.commands import clear_data


class ClearDataTest(test.TestCase):

    def test_happy(self):
        trope_tag = factories.TropeTagFactory.create()
        trope = factories.TropeFactory.create(tags=[trope_tag])
        genre = factories.GenreFactory.create()
        creator = factories.CreatorFactory.create()
        work = factories.WorkFactory.create(
            tropes=[trope], genres=[genre], creator=creator)
        command = clear_data.Command()

        with mock.patch.object(
                command,
                '_get_confirmation',
                return_value=command.confirmation_match_string):
            command.handle()

        for model_inst in (trope_tag, trope, genre, creator, work):
            self.assertFalse(
                model_inst.__class__.objects.filter(
                    id=model_inst.id).exists())

    def test_bad_confirmation(self):
        trope = factories.TropeFactory.create()
        command = clear_data.Command()
        with mock.patch.object(
                command,
                '_get_confirmation',
                return_value='no thanks'):
            command.handle()
        # Nothing deleted.
        self.assertTrue(trope.__class__.objects.filter(id=trope.id).exists())
