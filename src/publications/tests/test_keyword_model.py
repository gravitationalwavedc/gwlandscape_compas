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

        try:
            Keyword.delete_keyword(o.id)
            self.fail("Keyword was deleted successfully when it should have failed")
        except Keyword.DoesNotExist:
            pass
