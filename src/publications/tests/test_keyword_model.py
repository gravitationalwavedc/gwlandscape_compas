from django.db import IntegrityError
from django.test import testcases

from publications.models import Keyword


class TestKeywordModel(testcases.TestCase):
    def test_create(self):
        Keyword.create_keyword('test')
        self.assertEqual(1, Keyword.objects.all().count())
        self.assertTrue('test', Keyword.objects.last().tag)

        try:
            Keyword.create_keyword('test')
            self.fail("Should have raised IntegrityError")
        except IntegrityError:
            pass

    def test_delete(self):
        o = Keyword.create_keyword('test')
        Keyword.delete_keyword(o.id)

        with self.assertRaises(
            Keyword.DoesNotExist,
            msg="Keyword was deleted successfully when it should have failed"
        ):
            Keyword.delete_keyword(o.id)

    def test_update(self):
        o = Keyword.create_keyword('test')

        self.assertEqual(o.tag, 'test')

        Keyword.update_keyword(o.id, 'new')
        o.refresh_from_db()

        self.assertEqual(o.tag, 'new')
