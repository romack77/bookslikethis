import json
from unittest import mock

from core import test
from core import factories


class SearchViewTest(test.TestCase):

    def test_happy(self):
        tag = factories.TropeTagFactory.create()
        trope = factories.TropeFactory.create(tags=[tag])
        work = factories.WorkFactory.create(tropes=[trope])
        work_two = factories.WorkFactory.create(tropes=[trope], creator=None)

        response = self.client.get('/api/search/?works=%s' % work.name)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(
            data['results'],
            [{'id': work_two.id,
              'url': work_two.url,
              'name': work_two.name,
              'creator': None,
              'total_shared_tropes': 1,
              'tropes': [{
                  'id': trope.id,
                  'name': trope.name,
                  'url': trope.url,
                  'laconic_description': trope.laconic_description}],
              'genres': []}])

    def test_multiple_results(self):
        tag = factories.TropeTagFactory.create()
        trope = factories.TropeFactory.create(tags=[tag])
        trope_two = factories.TropeFactory.create(tags=[tag])
        trope_three = factories.TropeFactory.create(tags=[tag])
        work = factories.WorkFactory.create(
            tropes=[trope, trope_two, trope_three])
        work_two = factories.WorkFactory.create(
            tropes=[trope, trope_three], creator=None)
        work_three = factories.WorkFactory.create(tropes=[trope], creator=None)
        work_four = factories.WorkFactory.create(
            tropes=[trope, trope_two, trope_three], creator=None)

        response = self.client.get('/api/search/?works=%s' % work.name)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(
            data['results'],
            [{'id': work_four.id,
              'url': work_four.url,
              'name': work_four.name,
              'creator': None,
              'total_shared_tropes': 3,
              'tropes': mock.ANY,
              'genres': []},
             {'id': work_two.id,
              'url': work_two.url,
              'name': work_two.name,
              'creator': None,
              'total_shared_tropes': 2,
              'tropes': mock.ANY,
              'genres': []},
             {'id': work_three.id,
              'url': work_three.url,
              'name': work_three.name,
              'creator': None,
              'total_shared_tropes': 1,
              'tropes': [{
                  'id': trope.id,
                  'name': trope.name,
                  'url': trope.url,
                  'laconic_description': trope.laconic_description}],
              'genres': []},
             ])
        self.assertCountEqual(
            data['results'][0]['tropes'],
            [{'id': trope.id,
              'name': trope.name,
              'url': trope.url,
              'laconic_description': trope.laconic_description},
             {'id': trope_two.id,
              'name': trope_two.name,
              'url': trope_two.url,
              'laconic_description': trope_two.laconic_description},
             {'id': trope_three.id,
              'name': trope_three.name,
              'url': trope_three.url,
              'laconic_description': trope_three.laconic_description}])
        self.assertCountEqual(
            data['results'][1]['tropes'],
            [{'id': trope.id,
              'name': trope.name,
              'url': trope.url,
              'laconic_description': trope.laconic_description},
             {'id': trope_three.id,
              'name': trope_three.name,
              'url': trope_three.url,
              'laconic_description': trope_three.laconic_description}])

    def test_no_similar_works(self):
        tag = factories.TropeTagFactory.create()
        trope = factories.TropeFactory.create(tags=[tag])
        dissimilar_work = factories.WorkFactory.create(tropes=[trope])
        factories.WorkFactory.create()
        response = self.client.get(
            '/api/search/?works=%s' % dissimilar_work.name)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data['results'], [])

    def test_empty_db(self):
        response = self.client.get('/api/search/')
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data['results'], [])

    def test_missing_works_param(self):
        response = self.client.get('/api/search/')
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data['results'], [])

        response = self.client.get('/api/search/?works=')
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data['results'], [])

    def test_bad_work_name(self):
        response = self.client.get('/api/search/?works=fake')
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data['results'], [])

    def test_query_param(self):
        tag = factories.TropeTagFactory.create()
        trope = factories.TropeFactory.create(tags=[tag])
        work = factories.WorkFactory.create(tropes=[trope])
        work_two = factories.WorkFactory.create(tropes=[trope], creator=None)

        response = self.client.get('/api/search/?query=%s' % work.name)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(
            data['results'],
            [{'id': work_two.id,
              'url': work_two.url,
              'name': work_two.name,
              'creator': None,
              'total_shared_tropes': 1,
              'tropes': [{
                  'id': trope.id,
                  'name': trope.name,
                  'url': trope.url,
                  'laconic_description': trope.laconic_description}],
              'genres': []}])


class AutocompleteViewTest(test.TestCase):

    def test_happy(self):
        work = factories.WorkFactory.create(name='war')
        work_two = factories.WorkFactory.create(name='war and peace')
        work_three = factories.WorkFactory.create(name='something different')
        response = self.client.get('/api/autocomplete/?query=%s' % work.name)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(
            data['suggestions'],
            [{'name': work.name},
             {'name': work_two.name}])

        response = self.client.get(
            '/api/autocomplete/?query=%s' % work_three.name)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(
            data['suggestions'],
            [{'name': work_three.name}])

    def test_no_results(self):
        factories.WorkFactory.create(name='aaa')
        query = 'zzz'
        response = self.client.get('/api/autocomplete/?query=%s' % query)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data['suggestions'], [])

    def test_empty_query(self):
        response = self.client.get('/api/autocomplete/?query=')
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data['suggestions'], [])

    def test_missing_query_param(self):
        response = self.client.get('/api/autocomplete/')
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data['suggestions'], [])

