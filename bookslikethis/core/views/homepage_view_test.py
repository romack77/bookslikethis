from core import test


class HomepageViewTest(test.TestCase):

    def test_happy(self):
        response = self.client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Books Like This', str(response.content))
