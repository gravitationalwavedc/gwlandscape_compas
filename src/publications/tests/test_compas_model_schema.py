import humps
from django.contrib.auth import get_user_model
from django.test import override_settings
from graphql_relay import to_global_id

from compasui.tests.testcases import CompasTestCase
from publications.models import CompasModel

User = get_user_model()


class TestCompasModelSchema(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(username="buffy", first_name="buffy", last_name="summers")

        self.add_compas_model_mutation = """
            mutation AddCompasModelMutation($input: AddCompasModelMutationInput!) {
                addCompasModel(input: $input) {
                    id
                }
            }
        """

        self.delete_compas_model_mutation = """
            mutation DeleteCompasModelMutation($input: DeleteCompasModelMutationInput!) {
                deleteCompasModel(input: $input) {
                    result
                }
            }
        """

        self.model_query = """
            query {
                compasModels {
                    edges {
                        node {
                            name
                            summary
                            description
                        }
                    }
                }
            }
        """

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_add_compas_model_authenticated(self):
        self.client.authenticate(self.user)

        compas_model_input = {
            'input': {
                'name': 'test',
                'summary': 'summary',
                'description': 'description'
            }
        }

        response = self.client.execute(
            self.add_compas_model_mutation,
            compas_model_input
        )

        expected = {
            'addCompasModel': {
                'id': to_global_id('CompasModel', CompasModel.objects.last().id),
            }
        }

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(CompasModel.objects.filter(**compas_model_input['input']).count(), 1)

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_add_compas_model_authenticated_not_publication_manager(self):
        self.client.authenticate(self.user)

        compas_model_input = {
            'input': {
                'name': 'test',
                'summary': 'summary',
                'description': 'description'
            }
        }

        response = self.client.execute(
            self.add_compas_model_mutation,
            compas_model_input
        )

        expected = {
            'addCompasModel': None
        }

        self.assertEqual("You do not have permission to perform this action", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(CompasModel.objects.filter(**compas_model_input['input']).count(), 0)

    def test_add_compas_model_unauthenticated(self):
        compas_model_input = {
            'input': {
                'name': 'test',
                'summary': 'summary',
                'description': 'description'
            }
        }

        response = self.client.execute(
            self.add_compas_model_mutation,
            compas_model_input
        )

        expected = {
            'addCompasModel': None
        }

        self.assertEqual("You do not have permission to perform this action", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(CompasModel.objects.filter(**compas_model_input['input']).count(), 0)

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_delete_compas_model_authenticated(self):
        self.client.authenticate(self.user)

        kw = CompasModel.create_model('test', 'summary', 'description')

        compas_model_input = {
            'input': {
                'id': to_global_id('CompasModel', kw.id),
            }
        }

        response = self.client.execute(
            self.delete_compas_model_mutation,
            compas_model_input
        )

        expected = {
            'deleteCompasModel': {
                'result': True
            }
        }

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(CompasModel.objects.all().count(), 0)

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_delete_compas_model_authenticated_not_publication_manager(self):
        self.client.authenticate(self.user)

        kw = CompasModel.create_model('test', 'summary', 'description')

        compas_model_input = {
            'input': {
                'id': to_global_id('CompasModel', kw.id),
            }
        }

        response = self.client.execute(
            self.delete_compas_model_mutation,
            compas_model_input
        )

        expected = {
            'deleteCompasModel': None
        }

        self.assertEqual("You do not have permission to perform this action", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(CompasModel.objects.all().count(), 1)

    def test_delete_compas_model_unauthenticated(self):
        kw = CompasModel.create_model('test', 'summary', 'description')

        compas_model_input = {
            'input': {
                'id': to_global_id('CompasModel', kw.id),
            }
        }

        response = self.client.execute(
            self.delete_compas_model_mutation,
            compas_model_input
        )

        expected = {
            'deleteCompasModel': None
        }

        self.assertEqual("You do not have permission to perform this action", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(CompasModel.objects.all().count(), 1)

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_delete_compas_model_not_exists(self):
        self.client.authenticate(self.user)

        kw = CompasModel.create_model('test', 'summary', 'description')

        compas_model_input = {
            'input': {
                'id': to_global_id('CompasModel', kw.id+1),
            }
        }

        response = self.client.execute(
            self.delete_compas_model_mutation,
            compas_model_input
        )

        expected = {
            'deleteCompasModel': None
        }

        self.assertEqual("CompasModel matching query does not exist.", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(CompasModel.objects.all().count(), 1)

    def test_model_query_unauthenticated(self):
        compas_model_input = {
            'input': {
                'name': 'test',
                'summary': 'summary',
                'description': 'description'
            }
        }

        CompasModel.create_model(**humps.decamelize(compas_model_input['input']))

        response = self.client.execute(
            self.model_query
        )

        expected = {
            'compasModels': {
                'edges': [
                    {
                        'node': compas_model_input['input']
                    }
                ]
            }
        }

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)

    def test_model_query_authenticated(self):
        self.client.authenticate(self.user)

        compas_model_input = {
            'input': {
                'name': 'test',
                'summary': 'summary',
                'description': 'description'
            }
        }

        CompasModel.create_model(**humps.decamelize(compas_model_input['input']))

        response = self.client.execute(
            self.model_query
        )

        expected = {
            'compasModels': {
                'edges': [
                    {
                        'node': compas_model_input['input']
                    }
                ]
            }
        }

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)
