from django.contrib.auth import get_user_model
from django.test import override_settings
from graphql_relay import to_global_id

from compasui.tests.testcases import CompasTestCase
from publications.models import CompasModel
from publications.tests.test_utils import silence_errors

User = get_user_model()


class TestAddCompasModelSchema(CompasTestCase):
    def setUp(self):
        self.add_compas_model_mutation = """
            mutation AddCompasModelMutation($input: AddCompasModelMutationInput!) {
                addCompasModel(input: $input) {
                    id
                }
            }
        """

        self.compas_model_input = {
            "input": {
                "name": "test",
                "summary": "summary",
                "description": "description",
            }
        }

        self.null_output = {"addCompasModel": None}

    def execute_query(self):
        return self.query(
            self.add_compas_model_mutation, input_data=self.compas_model_input["input"]
        )

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_add_compas_model_authenticated(self):
        self.authenticate()

        response = self.execute_query()

        expected = {
            "addCompasModel": {
                "id": to_global_id("CompasModelNode", CompasModel.objects.last().id),
            }
        }

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(
            CompasModel.objects.filter(**self.compas_model_input["input"]).count(), 1
        )

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_add_compas_model_authenticated_not_publication_manager(self):
        self.authenticate()

        response = self.execute_query()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0]["message"],
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertEqual(
            CompasModel.objects.filter(**self.compas_model_input["input"]).count(), 0
        )

    @silence_errors
    def test_add_compas_model_unauthenticated(self):
        response = self.execute_query()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0]["message"],
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertEqual(
            CompasModel.objects.filter(**self.compas_model_input["input"]).count(), 0
        )


class TestDeleteCompasModelSchema(CompasTestCase):
    def setUp(self):
        self.model = CompasModel.create_model("test", "summary", "description")

        self.delete_compas_model_mutation = """
            mutation DeleteCompasModelMutation($input: DeleteCompasModelMutationInput!) {
                deleteCompasModel(input: $input) {
                    result
                }
            }
        """

        self.compas_model_input = {
            "input": {
                "id": to_global_id("CompasModelNode", self.model.id),
            }
        }

        self.null_output = {"deleteCompasModel": None}

    def execute_query(self):
        return self.query(
            self.delete_compas_model_mutation, input_data=self.compas_model_input["input"]
        )

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_delete_compas_model_authenticated(self):
        self.authenticate()

        response = self.execute_query()

        expected = {"deleteCompasModel": {"result": True}}

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(CompasModel.objects.all().count(), 0)

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_delete_compas_model_authenticated_not_publication_manager(self):
        self.authenticate()

        response = self.execute_query()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0]["message"],
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertEqual(CompasModel.objects.all().count(), 1)

    @silence_errors
    def test_delete_compas_model_unauthenticated(self):
        response = self.execute_query()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0]["message"],
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertEqual(CompasModel.objects.all().count(), 1)

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_delete_compas_model_not_exists(self):
        self.authenticate()

        self.compas_model_input["input"]["id"] = to_global_id(
            "CompasModelNode", self.model.id + 1
        )
        response = self.execute_query()

        self.assertEqual(
            "CompasModel matching query does not exist.", response.errors[0]["message"]
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertEqual(CompasModel.objects.all().count(), 1)


class TestUpdateCompasModelSchema(CompasTestCase):
    def setUp(self):
        self.model = CompasModel.create_model("test", "summary", "description")

        self.update_compas_model_mutation = """
            mutation UpdateCompasModelMutation($input: UpdateCompasModelMutationInput!) {
                updateCompasModel(input: $input) {
                    result
                }
            }
        """

        self.initial_model_fields = self.get_model_fields(self.model)
        self.updated_model_fields = {
            "name": "new test",
            "summary": "new summary",
            "description": "new description",
        }

        self.compas_model_input = {
            "input": {
                "id": to_global_id("CompasModelNode", self.model.id),
                **self.updated_model_fields,
            }
        }

        self.null_output = {"updateCompasModel": None}

    def get_model_fields(self, publication):
        return {
            field: getattr(self.model, field)
            for field in ["name", "summary", "description"]
        }

    def execute_query(self):
        return self.query(
            self.update_compas_model_mutation, input_data=self.compas_model_input["input"]
        )

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_update_compas_model_authenticated(self):
        self.authenticate()

        response = self.execute_query()
        self.model.refresh_from_db()

        expected = {"updateCompasModel": {"result": True}}

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)

        self.assertDictEqual(
            self.get_model_fields(self.model), self.updated_model_fields
        )

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_update_compas_model_authenticated_not_publication_manager(self):
        self.authenticate()

        response = self.execute_query()
        self.model.refresh_from_db()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0]["message"],
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertDictEqual(
            self.get_model_fields(self.model), self.initial_model_fields
        )

    @silence_errors
    def test_update_compas_model_unauthenticated(self):
        response = self.execute_query()
        self.model.refresh_from_db()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0]["message"],
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertDictEqual(
            self.get_model_fields(self.model), self.initial_model_fields
        )

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_update_compas_model_not_exists(self):
        self.authenticate()

        self.compas_model_input["input"]["id"] = to_global_id(
            "CompasModelNode", self.model.id + 1
        )
        response = self.execute_query()
        self.model.refresh_from_db()

        self.assertEqual(
            "CompasModel matching query does not exist.", response.errors[0]["message"]
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertDictEqual(
            self.get_model_fields(self.model), self.initial_model_fields
        )


class TestQueryCompasModelSchema(CompasTestCase):
    def setUp(self):
        self.model = CompasModel.create_model("test", "summary", "description")

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

        self.expected_output = {
            "compasModels": {
                "edges": [
                    {
                        "node": {
                            "name": "test",
                            "summary": "summary",
                            "description": "description",
                        }
                    }
                ]
            }
        }

    def test_model_query_unauthenticated(self):
        response = self.query(self.model_query)

        self.assertEqual(None, response.errors)
        self.assertDictEqual(self.expected_output, response.data)

    def test_model_query_authenticated(self):
        self.authenticate()

        response = self.query(self.model_query)

        self.assertEqual(None, response.errors)
        self.assertDictEqual(self.expected_output, response.data)
