from core import factories
from core import test


class TropeTest(test.TestCase):

    def test_get_tag_set(self):
        tag = factories.TropeTagFactory.create(name='plot')
        tag_two = factories.TropeTagFactory.create(name='setting')
        trope = factories.TropeFactory.create(tags=[tag, tag_two])
        self.assertEqual(
            trope.get_tag_set(), frozenset((tag.name, tag_two.name)))

    def test_get_tag_set_no_tags(self):
        trope = factories.TropeFactory.create()
        self.assertEqual(trope.get_tag_set(), frozenset())

    def test_set_tag_set(self):
        tag = factories.TropeTagFactory.create(name='plot')
        tag_two = factories.TropeTagFactory.create(name='setting')
        trope = factories.TropeFactory.create(tags=[tag])
        trope.set_tag_set({tag.name, tag_two.name})
        self.assertEqual(
            trope.get_tag_set(), frozenset((tag.name, tag_two.name)))

    def test_set_tag_set_no_tags(self):
        tag = factories.TropeTagFactory.create(name='plot')
        trope = factories.TropeFactory.create(tags=[tag])
        trope.set_tag_set(frozenset())
        self.assertEqual(trope.get_tag_set(), frozenset())
