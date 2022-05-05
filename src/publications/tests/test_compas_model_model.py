from django.test import testcases

from publications.models import CompasModel


class TestCompasModelModel(testcases.TestCase):
    def test_create(self):
        CompasModel.create_model('test', 'summary', 'description')
        self.assertEqual(1, CompasModel.objects.all().count())
        self.assertTrue('test', CompasModel.objects.last().name)
        self.assertTrue('summary', CompasModel.objects.last().summary)
        self.assertTrue('description', CompasModel.objects.last().description)

    def test_delete(self):
        o = CompasModel.create_model('test', 'summary', 'description')
        CompasModel.delete_model(o.id)

        try:
            CompasModel.delete_model(o.id)
            self.fail("CompasModel was deleted successfully when it should have failed")
        except CompasModel.DoesNotExist:
            pass
