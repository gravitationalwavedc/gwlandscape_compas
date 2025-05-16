from django.test import testcases

from publications.models import CompasModel


class TestCompasModelModel(testcases.TestCase):
    def setUp(self):
        self.model_input = {
            "name": "test",
            "summary": "summary",
            "description": "description",
        }

        self.update_model_input = {
            "name": "new_test",
            "summary": "new summary",
            "description": "new description",
        }

    def test_create(self):
        CompasModel.create_model(**self.model_input)
        self.assertEqual(1, CompasModel.objects.all().count())
        self.assertTrue("test", CompasModel.objects.last().name)
        self.assertTrue("summary", CompasModel.objects.last().summary)
        self.assertTrue("description", CompasModel.objects.last().description)

    def test_delete(self):
        o = CompasModel.create_model(**self.model_input)
        CompasModel.delete_model(o.id)

        with self.assertRaises(
            CompasModel.DoesNotExist,
            msg="CompasModel was deleted successfully when it should have failed",
        ):
            CompasModel.delete_model(o.id)

    def test_update_single(self):
        o = CompasModel.create_model(**self.model_input)

        for key, val in self.model_input.items():
            self.assertEqual(getattr(o, key), val)

            CompasModel.update_model(o.id, **{key: self.update_model_input[key]})
            o.refresh_from_db()

            self.assertEqual(getattr(o, key), self.update_model_input[key])

    def test_update_multi(self):
        o = CompasModel.create_model(**self.model_input)

        for key, val in self.model_input.items():
            self.assertEqual(getattr(o, key), val)

        CompasModel.update_model(o.id, **self.update_model_input)
        o.refresh_from_db()

        for key, val in self.update_model_input.items():
            self.assertEqual(getattr(o, key), val)
