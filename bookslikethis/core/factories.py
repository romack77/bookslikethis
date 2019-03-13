"""Model factories for unit tests."""
import logging

import factory
from factory import django

from core import models

logging.getLogger("factory").setLevel(logging.WARN)


class BaseFactory(django.DjangoModelFactory):
    pass


class TropeFactory(BaseFactory):
    class Meta:
        model = models.Trope
    url = factory.Sequence(lambda n: 'http://tropes.org/trope/%s' % n)
    name = factory.Sequence(lambda n: 'Trope %s' % n)
    laconic_description = 'laconic description'

    @factory.post_generation
    def tags(self, create, tags, **kwargs):
        if create and tags:
            for tag in tags:
                TropeTagMapFactory.create(trope_tag=tag, trope=self)


class TropeTagFactory(BaseFactory):
    class Meta:
        model = models.TropeTag
    name = 'plot'


class TropeTagMapFactory(BaseFactory):
    class Meta:
        model = models.TropeTagMap
    trope_tag = factory.SubFactory(TropeTagFactory)
    trope = factory.SubFactory(TropeFactory)


class GenreFactory(BaseFactory):
    class Meta:
        model = models.Genre
    url = factory.Sequence(lambda n: 'http://tropes.org/genre/%s' % n)
    name = factory.Sequence(lambda n: 'Genre %s' % n)


class CreatorFactory(BaseFactory):
    class Meta:
        model = models.Creator
    url = factory.Sequence(lambda n: 'http://tropes.org/creator/%s' % n)
    name = factory.Sequence(lambda n: 'Creator %s' % n)


class WorkFactory(BaseFactory):
    class Meta:
        model = models.Work
    url = factory.Sequence(lambda n: 'http://tropes.org/work/%s' % n)
    name = factory.Sequence(lambda n: 'Work %s' % n)
    creator = factory.SubFactory(CreatorFactory)

    @factory.post_generation
    def tropes(self, create, tropes, **kwargs):
        if create and tropes:
            for trope in tropes:
                TropeWorkFactory.create(trope=trope, work=self)

    @factory.post_generation
    def genres(self, create, genres, **kwargs):
        if create and genres:
            for genre in genres:
                GenreMapFactory.create(genre=genre, work=self)


class GenreMapFactory(BaseFactory):
    class Meta:
        model = models.GenreMap
    genre = factory.SubFactory(GenreFactory)
    work = factory.SubFactory(WorkFactory)


class TropeWorkFactory(BaseFactory):
    class Meta:
        model = models.TropeWork
    trope = factory.SubFactory(TropeFactory)
    work = factory.SubFactory(WorkFactory)
    snippet = 'snippet'
    is_spoiler = False
    is_ymmv = False
