from django.db import models
from django.utils import timezone

from core import db_index
from core import model_constants


class BaseModel(models.Model):
    """Provides audit timestamps."""

    created_date = models.DateTimeField(
        editable=False, default=timezone.now)
    modified_date = models.DateTimeField(
        editable=False, default=timezone.now)

    def save(self, *args, **kwargs):
        self.last_modified = timezone.now()
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Trope(BaseModel):
    """A trope. A pattern found in creative works."""
    url = models.URLField(db_index=True)
    name = models.CharField(max_length=model_constants.ENTITY_NAME_MAX_LENGTH)
    laconic_description = models.CharField(
        max_length=model_constants.LACONIC_DESCRIPTION_MAX_LENGTH)
    tags = models.ManyToManyField('TropeTag', through='TropeTagMap')
    referenced_tropes = models.ManyToManyField(
        'self', through='TropeTrope', symmetrical=False)

    def __init__(self, *args, **kwargs):
        self._tags = None
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_tag_set(self):
        """Gets tag names for this trope.

        Tags are fetched from the DB unless they were
        set directly via set_tag_set.

        Returns:
            frozenset of string tag names.
        """
        if self._tags is None:
            self._tags = frozenset(
                self.tags.all().values_list('name', flat=True))
        return self._tags

    def set_tag_set(self, tags):
        """Sets tag names for this trope.

        Args:
            tags: frozenset of string tag names.
        """
        self._tags = tags


class TropeTag(BaseModel):
    """A trope tag or category, e.g. 'plot' or 'setting'."""
    name = models.CharField(
        max_length=model_constants.ENTITY_NAME_MAX_LENGTH, db_index=True)

    def __str__(self):
        return self.name


class TropeTagMap(BaseModel):
    """Connections between tropes and and trope tags.

    A trope may any number of tags.
    """
    trope_tag = models.ForeignKey(TropeTag, on_delete=models.CASCADE)
    trope = models.ForeignKey(Trope, on_delete=models.CASCADE)

    def __str__(self):
        return '%s <-> %s' % (self.trope, self.trope_tag)


class Genre(BaseModel):
    """A genre category for works."""
    url = models.URLField()
    name = models.CharField(max_length=model_constants.ENTITY_NAME_MAX_LENGTH)
    parent_genre = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class GenreMap(BaseModel):
    """Connections between works and genres.

    A work may have any number of genres.
    """
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    work = models.ForeignKey('Work', on_delete=models.CASCADE)

    def __str__(self):
        return '%s <-> %s' % (self.genre, self.work)


class Creator(BaseModel):
    """The creator of a work."""
    url = models.URLField(db_index=True)
    name = models.CharField(max_length=model_constants.ENTITY_NAME_MAX_LENGTH)

    def __str__(self):
        return self.name


class Work(BaseModel):
    """A creative work."""
    url = models.URLField(db_index=True)
    name = models.CharField(
        db_index=True, max_length=model_constants.ENTITY_NAME_MAX_LENGTH)
    creator = models.ForeignKey(Creator, on_delete=models.SET_NULL, null=True)
    genres = models.ManyToManyField(Genre, through='GenreMap')
    tropes = models.ManyToManyField(Trope, through='TropeWork')

    class Meta:
        indexes = [db_index.GistIndexTrigrams(fields=['name'])]

    def __str__(self):
        return self.name


class TropeWork(BaseModel):
    """Connections between tropes and works."""
    trope = models.ForeignKey(Trope, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    snippet = models.TextField(default=None, null=True)
    is_spoiler = models.BooleanField(default=False)
    is_ymmv = models.BooleanField(default=False)

    def __str__(self):
        return '%s <-> %s' % (self.trope, self.work)


class TropeTrope(BaseModel):
    """Connections between tropes and tropes."""
    from_trope = models.ForeignKey(
        Trope, on_delete=models.CASCADE)
    to_trope = models.ForeignKey(
        Trope, on_delete=models.CASCADE, related_name='referenced_by_tropes')

    def __str__(self):
        return '%s -> %s' % (self.from_trope, self.to_trope)
