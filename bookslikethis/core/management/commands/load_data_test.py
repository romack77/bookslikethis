import json
import io

from core.management.commands import load_data
from core import models
from core import test


SAMPLE_TROPE_JSON = json.dumps({
    "url": "https://tvtropes.org/pmwiki/pmwiki.php/Main/TropeOne",
    "page_type": "trope",
    "page_namespace": "Main",
    "name": "Trope One",
    "referenced_tropes": [
        "https://tvtropes.org/pmwiki/pmwiki.php/Main/TropeTwo",
        "https://tvtropes.org/pmwiki/pmwiki.php/Main/TropeThree",
        "https://tvtropes.org/pmwiki/pmwiki.php/Main/TropeFour",
        "https://tvtropes.org/pmwiki/pmwiki.php/Main/TropeFive",
        "https://tvtropes.org/pmwiki/pmwiki.php/Main/TropeSix",
        "https://tvtropes.org/pmwiki/pmwiki.php/Main/TropeSeven"],
    "works": [
        {
            "url": "https://tvtropes.org/pmwiki/pmwiki.php/Literature/BookOne",
            "description": "Book One",
            "contains_spoilers": False,
            "contains_ymmv": False
        },
        {
            "url": "https://tvtropes.org/pmwiki/pmwiki.php/Literature/BookTwo",
            "description": "Book Two",
            "contains_spoilers": False,
            "contains_ymmv": False
        },
        {
            "url": "https://tvtropes.org/pmwiki/pmwiki.php/Literature/BookThree",
            "description": "Book Three",
            "contains_spoilers": False,
            "contains_ymmv": False
        },
        {
            "url": "https://tvtropes.org/pmwiki/pmwiki.php/Literature/BookFour",
            "description": "Book Four",
            "contains_spoilers": False,
            "contains_ymmv": False
        }],
    "subpage_urls": [
        "https://tvtropes.org/pmwiki/pmwiki.php/Main/TropeOne",
        "https://tvtropes.org/pmwiki/pmwiki.php/Laconic/TropeOne",
        "https://tvtropes.org/pmwiki/pmwiki.php/Quotes/TropeOne"],
    "laconic_description": "Trope One laconic description."
})

SAMPLE_TROPE_TWO_JSON = json.dumps({
    "url": "https://tvtropes.org/pmwiki/pmwiki.php/Main/TropeTwo",
    "page_type": "trope",
    "page_namespace": "Main",
    "name": "Trope Two",
    "referenced_tropes": [],
    "works": [],
    "subpage_urls": [],
    "laconic_description": "Trope Two laconic description"
})

SAMPLE_WORK_JSON = json.dumps({
    "url": "https://tvtropes.org/pmwiki/pmwiki.php/Literature/BookOne",
    "page_namespace": "Literature",
    "page_type": "work",
    "creator_name": "Author One",
    "creator_url": "https://tvtropes.org/pmwiki/pmwiki.php/Creator/AuthorOne",
    "title": "Book One",
    "tropes": [
        {
            "name": "Trope One",
            "url": "https://tvtropes.org/pmwiki/pmwiki.php/Main/TropeOne",
            "description": "Book One Trope One description.",
            "contains_spoilers": False,
            "contains_ymmv": False
        },
        {
            "name": "Other Trope",
            "url": "https://tvtropes.org/pmwiki/pmwiki.php/Main/OtherTrope",
            "description": "Book One Other Trope description.",
            "contains_spoilers": False,
            "contains_ymmv": False
        }]
})

SAMPLE_CREATOR_JSON = json.dumps({
    "url": "https://tvtropes.org/pmwiki/pmwiki.php/Creator/AuthorOne",
    "page_type": "creator",
    "title": "Author One",
    "works": [
        {"name": "Other One", "url": "https://tvtropes.org/pmwiki/pmwiki.php/Literature/OtherOne"},
        {"name": "Book One", "url": "https://tvtropes.org/pmwiki/pmwiki.php/Literature/BookOne"},
        {"name": "Other Two", "url": "https://tvtropes.org/pmwiki/pmwiki.php/Literature/OtherTwo"}],
    "tropes": []
})

SAMPLE_GENRE_JSON = json.dumps({
    "url": "https://tvtropes.org/pmwiki/pmwiki.php/Main/GenreOne",
    "page_namespace": "Main",
    "page_type": "genre",
    "genre": "Genre One",
    "parent_genre": None})

SAMPLE_TROPE_CATEGORY_JSON = json.dumps({
    "url": "https://tvtropes.org/pmwiki/pmwiki.php/Main/TropeOne",
    "name": "Trope One",
    "category": "plot",
    "page_type": "trope_category"})

SAMPLE_GENRE_MAP_JSON = json.dumps({
    "page_type": "genre_map",
    "genre": "Genre One",
    "work_url": "https://tvtropes.org/pmwiki/pmwiki.php/Literature/BookOne"})

SAMPLE_GENRE_SUB_ONE_JSON = json.dumps({
    "url": "https://tvtropes.org/pmwiki/pmwiki.php/Main/GenreSubOne",
    "page_namespace": "Main",
    "page_type": "genre",
    "genre": "Genre Sub One",
    "parent_genre": "Genre One"})

SAMPLE_GENRE_SUB_TWO_JSON = json.dumps({
    "url": "https://tvtropes.org/pmwiki/pmwiki.php/Main/GenreSubTwo",
    "page_namespace": "Main",
    "page_type": "genre",
    "genre": "Genre Sub Two",
    "parent_genre": "Genre One"})

SAMPLE_GENRE_MAP_SUB_ONE_JSON = json.dumps({
    "page_type": "genre_map",
    "genre": "Genre Sub One",
    "work_url": "https://tvtropes.org/pmwiki/pmwiki.php/Literature/BookOne"})

SAMPLE_GENRE_MAP_SUB_TWO_JSON = json.dumps({
    "page_type": "genre_map",
    "genre": "Genre Sub Two",
    "work_url": "https://tvtropes.org/pmwiki/pmwiki.php/Literature/BookOne"})


class LoadDataTest(test.TestCase):

    def test_happy(self):
        f = self._build_data_file((
            SAMPLE_TROPE_JSON, SAMPLE_WORK_JSON, SAMPLE_GENRE_JSON,
            SAMPLE_CREATOR_JSON, SAMPLE_TROPE_TWO_JSON,
            SAMPLE_TROPE_CATEGORY_JSON, SAMPLE_GENRE_MAP_JSON))
        command = load_data.Command()
        command.load_data([f])

        self.assertEqual(models.Trope.objects.count(), 2)
        self.assertEqual(models.Work.objects.count(), 1)
        self.assertEqual(models.Creator.objects.count(), 1)
        self.assertEqual(models.Genre.objects.count(), 1)
        self.assertEqual(models.GenreMap.objects.count(), 1)
        self.assertEqual(models.TropeTrope.objects.count(), 1)
        self.assertEqual(models.TropeWork.objects.count(), 1)
        self.assertEqual(models.TropeTag.objects.count(), 1)
        self.assertEqual(models.TropeTagMap.objects.count(), 1)

        work = models.Work.objects.all()[0]
        self.assertEqual(work.name, 'Book One')
        self.assertEqual(work.creator.name, 'Author One')

        trope = work.tropework_set.get(trope__name='Trope One')
        self.assertEqual(trope.snippet, 'Book One Trope One description.')
        self.assertFalse(trope.is_spoiler)
        self.assertFalse(trope.is_ymmv)
        self.assertEqual(
            trope.trope.laconic_description,
            'Trope One laconic description.')

    def test_genre_maps(self):
        f = self._build_data_file((
            SAMPLE_WORK_JSON,
            SAMPLE_GENRE_JSON,
            SAMPLE_GENRE_SUB_ONE_JSON,
            SAMPLE_GENRE_SUB_TWO_JSON,
            SAMPLE_GENRE_MAP_JSON,
            SAMPLE_GENRE_MAP_SUB_ONE_JSON,
            SAMPLE_GENRE_MAP_SUB_TWO_JSON))
        command = load_data.Command()
        command.load_data([f])
        self.assertEqual(models.GenreMap.objects.count(), 3)

    def _build_data_file(self, json_dicts):
        f = io.StringIO()
        for record in json_dicts:
            f.write(record)
            f.write('\n')
        f.seek(0)
        return f
