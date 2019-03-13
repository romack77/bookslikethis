from django.core.management import base

from core import models


class Command(base.BaseCommand):

    help = 'Clears content data from the database.'
    confirmation_match_string = 'delete'

    def handle(self, *args, **options):
        confirmation = self._get_confirmation()
        if confirmation != Command.confirmation_match_string:
            print('Aborting.')
            return

        print('Deleting...')
        self._delete_data()
        print('Finished.')

    def _get_confirmation(self):
        return input(
            ('This will permanently delete all trope and creative '
             'work data from the database. Type "%s" to confirm.\n') % (
                Command.confirmation_match_string))

    def _delete_data(self):
        models.TropeWork.objects.all().delete()
        models.TropeTrope.objects.all().delete()
        models.TropeTagMap.objects.all().delete()
        models.TropeTag.objects.all().delete()
        models.Trope.objects.all().delete()

        models.GenreMap.objects.all().delete()
        models.Work.objects.all().delete()
        models.Creator.objects.all().delete()
        models.Genre.objects.all().delete()
