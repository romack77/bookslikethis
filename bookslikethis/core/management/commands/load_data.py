import json
import os
import tempfile
from urllib import request

from django.core.management import base
from django.core import validators
from django.core import exceptions
from django.utils import text

from core import model_constants
from core import models


class Command(base.BaseCommand):
    """Populates db data from JSON Lines files.

    This is not idempotent and is best run in one batch against
    an empty DB. There is no support for updating or merging with
    existing records. The clear_data script can reset the DB.
    """

    help = 'Populates the database.'

    # Works tagged with any of these genres will be omitted.
    EXCLUDED_GENRES = {'Sacred Literature'}

    # How many records to process and write to the DB at a time.
    BATCH_SIZE = 200

    def add_arguments(self, parser):
        parser.add_argument(
            'file', nargs='+', type=str,
            help='List of local jsonl data files or URLs.')
        parser.add_argument(
            '--skip-trope-self-refs',
            help='Omits trope to trope links.',
            action='store_true')

    def _get_files(self, file_names, temp_dir):
        """Fetches file objects.

        Args:
            file_names: List of string local file names or URLs.
            temp_dir: String path of directory to use for temp data.

        Returns:
            List of file-like objects.
        """
        validate_url = validators.URLValidator()
        files = []
        for i, file_name in enumerate(file_names):
            try:
                validate_url(file_name)
            except exceptions.ValidationError:
                pass
            else:
                # Download to local file system first.
                url = file_name
                print('Fetching %s...' % url)
                file_name = os.path.join(temp_dir, str(i))
                request.urlretrieve(url, file_name)
            files.append(open(file_name, 'r'))
        return files

    def handle(self, *args, **options):
        """Main entry point for this command.

        Kwargs:
            file: List of string file names for JSON lines files.
                See test_load_data for json format examples.
                Records can be of mixed page type, and in any order.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            files = self._get_files(options['file'], temp_dir)
            self.load_data(
                files,
                skip_trope_self_refs=options.get('skip_trope_self_refs'))
            for f in files:
                try:
                    f.close()
                except (IOError, OSError, PermissionError) as e:
                    print('Failed to close %s: "%s"' % (f.name, e))

    def load_data(self, files, skip_trope_self_refs=False):
        """Populates the DB with data from files.

        Args:
            files: List of file like objects with JSON lines data. See
                test_load_data for example record format.
                Records can be of mixed page type, and in any order.
            skip_trope_self_refs: Boolean, whether to load trope-to-trope
                references.
        """
        # Save the base records to the DB, without any foreign key relationships,
        # so that records don't need to be in topographic order.
        self.load_records(files)

        # Run through the records again, adding any foreign key relationships.
        self.load_relationships(files, skip_trope_self_refs)

        # Load anything depending on foreign key relationships.
        self.load_2nd_degree_relationships(files)

        # Remove any works associated with excluded genres.
        self.remove_excluded_genres()

        # Remove any orphan genre records.
        self.remove_orphan_genres()

    def walk_jsonl_files(self, files):
        """Yields dicts from JSON lines files.

        Args:
            files: List of file like objects with JSON lines data. See
                test_load_data for example record format.

        Yields:
            Dictionaries.
        """
        for f in files:
            for line in f:
                yield json.loads(line)

    def load_record_batches(self, files):
        """Builds unsaved models from json records, returning a batch at a time.

        Args:
            files: List of file like objects with JSON lines data. See
                test_load_data for example record format.

        Returns:
            List of Trope, Work, Genre, or Creator record dicts, subject to BATCH_SIZE.
            A single batch is always of the same record type, and never empty.
        """
        page_type_to_records = {
            'trope': [],
            'work': [],
            'genre': [],
            'genre_map': [],
            'creator': [],
            'trope_category': []}
        for record in self.walk_jsonl_files(files):
            if record['page_type'] in page_type_to_records:
                records = page_type_to_records[record['page_type']]
                records.append(record)
                if len(records) >= Command.BATCH_SIZE:
                    yield records
                    page_type_to_records[record['page_type']] = []
            else:
                self.stdout.write(self.style.ERROR(
                    'Did not recognize page type %s' % record['page_type']))
        for records in page_type_to_records.values():
            if records:
                yield records

    def load_records(self, files):
        """Saves base records, without any foreign key relationships.

        Args:
            files: List of file like objects with JSON lines data. See
                test_load_data for example record format.
        """
        record_count = 0
        for record_batch in self.load_record_batches(files):
            if record_batch[0]['page_type'] == 'trope':
                self.load_tropes(record_batch)
            elif record_batch[0]['page_type'] == 'work':
                self.load_works(record_batch)
            elif record_batch[0]['page_type'] == 'genre':
                self.load_genres(record_batch)
            elif record_batch[0]['page_type'] == 'creator':
                self.load_creators(record_batch)
            elif record_batch[0]['page_type'] == 'trope_category':
                self.load_trope_tags(record_batch)
            else:
                continue
            record_count += len(record_batch)
            self.stdout.write(self.style.SUCCESS(
                'Loaded %s %s records. %s records so far.' % (
                    len(record_batch), record_batch[0]['page_type'],
                    record_count)))
        [f.seek(0) for f in files]

    def load_relationships(self, files, skip_trope_self_refs):
        """Populates foreign key relationships.

        This assumes the referenced records already exist because
        load_records was already run.

        Args:
            files: List of file like objects with JSON lines data. See
                test_load_data for example record format.
            skip_trope_self_refs: Boolean, whether to load trope-to-trope
                references.
        """
        record_count = 0
        for record_batch in self.load_record_batches(files):
            if record_batch[0]['page_type'] == 'trope':
                self.load_trope_relationships(
                    record_batch, skip_trope_self_refs)
            elif record_batch[0]['page_type'] == 'work':
                self.load_work_relationships(record_batch)
            elif record_batch[0]['page_type'] == 'genre':
                self.load_genre_relationships(record_batch)
            elif record_batch[0]['page_type'] == 'trope_category':
                self.load_trope_tag_relationships(record_batch)
            else:
                # Other records types don't specify any relationships.
                continue
            record_count += len(record_batch)
            self.stdout.write(self.style.SUCCESS(
                'Loaded relationships for %s %s records. %s records so far' % (
                    len(record_batch), record_batch[0]['page_type'],
                    record_count)))
        [f.seek(0) for f in files]

    def load_2nd_degree_relationships(self, files):
        """Populates relationships that depend on existing foreign keys.

        This assumes that load_records and load_relationships were already run.

        Args:
            files: List of file like objects with JSON lines data. See
                test_load_data for example record format.
        """
        record_count = 0
        for record_batch in self.load_record_batches(files):
            if record_batch[0]['page_type'] == 'genre_map':
                self.load_genre_map_relationships(record_batch)
            else:
                continue
            record_count += len(record_batch)
            self.stdout.write(self.style.SUCCESS(
                ('Loaded 2nd degree relationships for %s %s records. '
                 '%s records so far') % (
                    len(record_batch), record_batch[0]['page_type'],
                    record_count)))
        [f.seek(0) for f in files]

    def load_tropes(self, records):
        """Creates Trope records."""
        tropes = []
        for record in records:
            laconic = text.Truncator(
                record['laconic_description'] or '').chars(
                    model_constants.LACONIC_DESCRIPTION_MAX_LENGTH - 1)
            tropes.append(models.Trope(
                name=record['name'] or '',
                url=record['url'],
                laconic_description=laconic))
        models.Trope.objects.bulk_create(tropes)

    def load_works(self, records):
        """Creates Work records."""
        works = []
        for record in records:
            works.append(models.Work(
                name=record['title'] or '',
                url=record['url']))
        models.Work.objects.bulk_create(works)

    def load_genres(self, records):
        """Creates Genre records."""
        lowered_url_to_new_genre = {}
        existing_lowered_to_cased = {
            u.lower(): u
            for u in models.Genre.objects.all().values_list('url', flat=True)}
        for record in records:
            if not record['genre']:
                # Bad record.
                continue
            elif record['url'].lower() in existing_lowered_to_cased:
                # Genre exists.
                existing_url = existing_lowered_to_cased[record['url'].lower()]
                if (Command.count_capital_letters(record['url']) >
                        Command.count_capital_letters(existing_url)):
                    # Genre exists, but its URL differs by case, e.g. /FanWebComics
                    # vs /FanWebcomics. Merge these records, keeping the URL with more
                    # capital letters, which is almost always the correct/canonical one.
                    if existing_url in lowered_url_to_new_genre:
                        # Update the unsaved record.
                        new_genre = lowered_url_to_new_genre[record['url'].lower()]
                        new_genre.url = record['url']
                        new_genre.name = record['genre']
                    else:
                        # Update the DB record.
                        existing_genre = models.Genre.objects.get(
                            url__iexact=record['url'].lower())
                        existing_genre.url = record['url']
                        existing_genre.name = record['genre']
                        existing_genre.save()
            else:
                # New genre.
                lowered_url_to_new_genre[record['url'].lower()] = models.Genre(
                    name=record['genre'],
                    url=record['url'])
                existing_lowered_to_cased[record['url'].lower()] = record['url']
        if lowered_url_to_new_genre:
            models.Genre.objects.bulk_create(lowered_url_to_new_genre.values())

    @staticmethod
    def count_capital_letters(string):
        """Gets the number of capitals in a string."""
        return sum(1 for c in string if c.isupper())

    def load_creators(self, records):
        """Creates Creator records."""
        creators = []
        for record in records:
            creators.append(models.Creator(
                name=record['title'] or '',
                url=record['url']))
        models.Creator.objects.bulk_create(creators)

    def load_trope_tags(self, records):
        """Creates TropeTag records."""
        tag_names = {r['category'] for r in records}
        existing_tag_names = set(models.TropeTag.objects.filter(
            name__in=tag_names).values_list('name', flat=True))
        new_trope_tags = []
        for tag_name in tag_names:
            if tag_name not in existing_tag_names:
                new_trope_tags.append(models.TropeTag(name=tag_name))
        models.TropeTag.objects.bulk_create(new_trope_tags)

    def load_trope_relationships(self, records, skip_trope_self_refs):
        """Populates relationships specified in Trope records.

        Args:
            records: List of record dicts.
            skip_trope_self_refs: Boolean, whether to load trope-to-trope
                references.
        """
        trope_tropes = []
        trope_works = []
        url_to_trope = {
            t.url: t for t in models.Trope.objects.filter(
                url__in=[r['url'] for r in records])}
        for record in records:
            trope = url_to_trope[record['url']]
            if not skip_trope_self_refs:
                for ref_trope in models.Trope.objects.filter(
                        url__in=record['referenced_tropes']):
                    trope_tropes.append(models.TropeTrope(
                        from_trope=trope, to_trope=ref_trope))

            work_url_to_record = {w['url']: w for w in record['works']}
            existing_trope_works = set(
                models.TropeWork.objects.filter(
                    trope=trope).select_related('work').values_list(
                    'work__url', flat=True))
            for work in models.Work.objects.filter(
                    url__in=work_url_to_record.keys()):
                # Add any trope-work relationships not already added
                # by load_work_relationships.
                if work.url not in existing_trope_works:
                    trope_works.append(models.TropeWork(
                        trope=trope,
                        work=work,
                        snippet=work_url_to_record[work.url]['description'],
                        is_spoiler=work_url_to_record[work.url]['contains_spoilers'],
                        is_ymmv=work_url_to_record[work.url]['contains_ymmv']))

        if trope_tropes:
            models.TropeTrope.objects.bulk_create(trope_tropes)
        if trope_works:
            models.TropeWork.objects.bulk_create(trope_works)

    def load_work_relationships(self, records):
        """Populates relationships specified in Work records."""
        url_to_work = {
            w.url: w for w in models.Work.objects.filter(
                url__in=[r['url'] for r in records])}
        url_to_creator = {
            c.url: c for c in models.Creator.objects.filter(
                url__in=[r['creator_url'] for r in records])}

        trope_works = []
        for record in records:
            work = url_to_work[record['url']]

            if record['creator_url'] and record['creator_url'] in url_to_creator:
                work.creator = url_to_creator[record['creator_url']]
                work.save()

            trope_url_to_record = {t['url']: t for t in record['tropes']}
            existing_trope_works = {
                tw.work.url: tw for tw in models.TropeWork.objects.filter(
                    work=work).select_related('work')}
            for trope in models.Trope.objects.filter(
                    url__in=trope_url_to_record.keys()):
                if work.url in existing_trope_works:
                    # Replace the description since work pages virtually always
                    # have more detailed descriptions.
                    trope_work = existing_trope_works[work.url]
                    trope_work.snippet = trope_url_to_record[trope.url][
                        'description']
                    trope_work.is_spoiler |= trope_url_to_record[trope.url][
                        'contains_spoilers']
                    trope_work.is_ymmv |= trope_url_to_record[trope.url][
                        'contains_ymmv']
                    trope_work.save()
                else:
                    trope_works.append(models.TropeWork(
                        trope=trope,
                        work=work,
                        snippet=trope_url_to_record[trope.url]['description'],
                        is_spoiler=trope_url_to_record[trope.url]['contains_spoilers'],
                        is_ymmv=trope_url_to_record[trope.url]['contains_ymmv']))

        models.TropeWork.objects.bulk_create(trope_works)

    def load_genre_relationships(self, records):
        """Populates relationships specified in Genre records."""
        for record in records:
            if record['parent_genre'] is None:
                continue
            genre = models.Genre.objects.get(url__iexact=record['url'])
            genre.parent_genre = models.Genre.objects.get(
                name=record['parent_genre'])
            genre.save()

    def load_genre_map_relationships(self, records):
        """Populates relationships specified in Genre map records.

        Can handle duplicate and existing records.
        """
        name_to_genre = {
            g.name: g for g in models.Genre.objects.all().select_related(
                'parent_genre')}
        existing_genre_maps = set(
            models.GenreMap.objects.filter(
                work__url__in=[r['work_url'] for r in records]).select_related(
                'work', 'genre').values_list('work__url', 'genre__name'))
        missing_maps = {
            (r['work_url'], r['genre']) for r in records}.difference(
            existing_genre_maps)
        url_to_work = {
            w.url: w for w in models.Work.objects.filter(
                url__in=[url for (url, _) in missing_maps])}
        genre_maps = []
        for work_url, genre_name in missing_maps:
            if (work_url not in url_to_work or
                    genre_name not in name_to_genre):
                continue
            genre = name_to_genre[genre_name]
            if (work_url, genre_name) not in existing_genre_maps:
                genre_maps.append(models.GenreMap(
                    genre=genre,
                    work=url_to_work[work_url]))
                existing_genre_maps.add((work_url, genre_name))
            # Tag works at all levels of the genre hierarchy.
            # E.g., if High Fantasy is a sub genre of Fantasy,
            # then a High Fantasy work will have a GenreMap record
            # linking it to both High Fantasy and Fantasy.
            parent_genre = genre.parent_genre
            while parent_genre is not None:
                if (work_url, parent_genre.name) not in existing_genre_maps:
                    genre_maps.append(
                        models.GenreMap(
                            genre=parent_genre, work=url_to_work[work_url]))
                    existing_genre_maps.add((work_url, parent_genre.name))
                parent_genre = parent_genre.parent_genre
        if genre_maps:
            models.GenreMap.objects.bulk_create(genre_maps)

    def load_trope_tag_relationships(self, records):
        """Populates relationships specified in trope tag records.

        Can handle duplicate and existing records.
        """
        tag_names = {r['category'] for r in records}
        name_to_tag = {
            t.name: t for t in models.TropeTag.objects.filter(
                name__in=tag_names)}
        existing_tag_maps = set(
            models.TropeTagMap.objects.filter(
                trope_tag__in=name_to_tag.values(),
                trope__url__in=[r['url'] for r in records]).select_related(
                'trope', 'tropetag').values_list('trope__url', 'trope_tag__name'))
        missing_maps = {
            (r['url'], r['category']) for r in records}.difference(
            existing_tag_maps)
        url_to_trope = {t.url: t for t in models.Trope.objects.filter(
            url__in=[url for (url, _) in missing_maps])}
        tag_maps = []
        for url, category in missing_maps:
            if category in name_to_tag and url in url_to_trope:
                tag_maps.append(models.TropeTagMap(
                    trope=url_to_trope[url],
                    trope_tag=name_to_tag[category]))
        if tag_maps:
            models.TropeTagMap.objects.bulk_create(tag_maps)

    def remove_excluded_genres(self):
        """Clears any works associated with excluded genres."""
        models.Work.objects.filter(
            genres__name__in=Command.EXCLUDED_GENRES).delete()

    def remove_orphan_genres(self):
        """Clears any genre records not referenced by works or other genres."""
        parent_genres = list(models.Genre.objects.all().values_list(
            'parent_genre_id', flat=True))
        work_genres = list(models.GenreMap.objects.all().order_by(
            'genre_id').distinct().values_list(
            'genre_id', flat=True))
        referenced_genres = [g for g in parent_genres + work_genres if g is not None]
        models.Genre.objects.exclude(id__in=referenced_genres).delete()
