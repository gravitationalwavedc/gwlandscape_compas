from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import override_settings
from graphql_relay import to_global_id

from compasui.tests.testcases import CompasTestCase
from publications.models import Keyword
from publications.tests.test_utils import silence_errors

User = get_user_model()


class TestAddKeywordSchema(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="buffy", first_name="buffy", last_name="summers"
        )

        self.add_keyword_mutation = """
            mutation AddKeywordMutation($input: AddKeywordMutationInput!) {
                addKeyword(input: $input) {
                    id
                }
            }
        """

        self.keyword_input = {"input": {"tag": "test"}}

    def execute_query(self):
        return self.client.execute(self.add_keyword_mutation, self.keyword_input)

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_add_keyword_authenticated(self):
        self.client.authenticate(self.user)

        response = self.execute_query()

        expected = {
            "addKeyword": {
                "id": to_global_id("Keyword", Keyword.objects.last().id),
            }
        }

        self.assertIsNone(response.errors)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(
            Keyword.objects.filter(tag=self.keyword_input["input"]["tag"]).count(), 1
        )

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_add_keyword_authenticated_not_publication_manager(self):
        self.client.authenticate(self.user)

        response = self.execute_query()

        expected = {"addKeyword": None}

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(expected, response.data)

        self.assertEqual(
            Keyword.objects.filter(tag=self.keyword_input["input"]["tag"]).count(), 0
        )

    @silence_errors
    def test_add_keyword_unauthenticated(self):
        response = self.execute_query()

        expected = {"addKeyword": None}

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(expected, response.data)

        self.assertEqual(
            Keyword.objects.filter(tag=self.keyword_input["input"]["tag"]).count(), 0
        )

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_add_keyword_duplicate_tag(self):
        self.client.authenticate(self.user)

        self.execute_query()

        with transaction.atomic():
            response = self.execute_query()

        expected = {"addKeyword": None}

        self.assertEqual(
            "UNIQUE constraint failed: publications_keyword.tag",
            response.errors[0].message,
        )
        self.assertDictEqual(expected, response.data)

        self.assertEqual(
            Keyword.objects.filter(tag=self.keyword_input["input"]["tag"]).count(), 1
        )


class TestDeleteKeywordSchema(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="buffy", first_name="buffy", last_name="summers"
        )
        self.kw = Keyword.create_keyword("test")

        self.delete_keyword_mutation = """
            mutation DeleteKeywordMutation($input: DeleteKeywordMutationInput!) {
                deleteKeyword(input: $input) {
                    result
                }
            }
        """

        self.keyword_input = {
            "input": {
                "id": to_global_id("Keyword", self.kw.id),
            }
        }

    def execute_query(self):
        return self.client.execute(self.delete_keyword_mutation, self.keyword_input)

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_delete_keyword_authenticated(self):
        self.client.authenticate(self.user)

        response = self.execute_query()

        expected = {"deleteKeyword": {"result": True}}

        self.assertIsNone(response.errors)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(Keyword.objects.all().count(), 0)

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_delete_keyword_authenticated_not_publication_manager(self):
        self.client.authenticate(self.user)

        response = self.execute_query()

        expected = {"deleteKeyword": None}

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(expected, response.data)

        self.assertEqual(Keyword.objects.all().count(), 1)

    @silence_errors
    def test_delete_keyword_unauthenticated(self):
        response = self.execute_query()

        expected = {"deleteKeyword": None}

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(expected, response.data)

        self.assertEqual(Keyword.objects.all().count(), 1)

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_delete_keyword_not_exists(self):
        self.client.authenticate(self.user)

        self.keyword_input["input"]["id"] = to_global_id("Keyword", self.kw.id + 1)

        response = self.execute_query()

        expected = {"deleteKeyword": None}

        self.assertEqual(
            "Keyword matching query does not exist.", response.errors[0].message
        )
        self.assertDictEqual(expected, response.data)

        self.assertEqual(Keyword.objects.all().count(), 1)


class TestUpdateKeywordSchema(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="buffy", first_name="buffy", last_name="summers"
        )
        self.kw = Keyword.create_keyword("test")

        self.update_keyword_mutation = """
            mutation UpdateKeywordMutation($input: UpdateKeywordMutationInput!) {
                updateKeyword(input: $input) {
                    result
                }
            }
        """

        self.keyword_input = {
            "input": {"id": to_global_id("Keyword", self.kw.id), "tag": "new_test"}
        }

    def execute_query(self):
        return self.client.execute(self.update_keyword_mutation, self.keyword_input)

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_update_keyword_authenticated(self):
        self.client.authenticate(self.user)

        response = self.execute_query()

        expected = {"updateKeyword": {"result": True}}

        self.assertIsNone(response.errors)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(Keyword.objects.first().tag, "new_test")

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_update_keyword_authenticated_not_publication_manager(self):
        self.client.authenticate(self.user)

        response = self.execute_query()

        expected = {"updateKeyword": None}

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(expected, response.data)

        self.assertEqual(Keyword.objects.first().tag, "test")

    @silence_errors
    def test_update_keyword_unauthenticated(self):
        response = self.execute_query()

        expected = {"updateKeyword": None}

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(expected, response.data)

        self.assertEqual(Keyword.objects.first().tag, "test")

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_update_keyword_not_exists(self):
        self.client.authenticate(self.user)

        self.keyword_input["input"]["id"] = to_global_id("Keyword", self.kw.id + 1)

        response = self.execute_query()

        expected = {"updateKeyword": None}

        self.assertEqual(
            "Keyword matching query does not exist.", response.errors[0].message
        )
        self.assertDictEqual(expected, response.data)

        self.assertEqual(Keyword.objects.first().tag, "test")


class TestQueryKeywordSchema(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="buffy", first_name="buffy", last_name="summers"
        )
        Keyword.create_keyword("test")
        Keyword.create_keyword("test1")
        Keyword.create_keyword("test2")
        Keyword.create_keyword("first")

        self.keyword_query = """
            query {
                keywords {
                    edges {
                        node {
                            id
                            tag
                        }
                    }
                }
            }
        """

    @silence_errors
    def test_keyword_query_unauthenticated(self):
        response = self.client.execute(self.keyword_query)

        expected = {
            "keywords": {
                "edges": [
                    {"node": {"tag": "first", "id": to_global_id("KeywordNode", 4)}},
                    {"node": {"tag": "test", "id": to_global_id("KeywordNode", 1)}},
                    {"node": {"tag": "test1", "id": to_global_id("KeywordNode", 2)}},
                    {"node": {"tag": "test2", "id": to_global_id("KeywordNode", 3)}},
                ]
            }
        }

        self.assertIsNone(response.errors)
        self.assertDictEqual(expected, response.data)

    def test_keyword_query_authenticated(self):
        self.client.authenticate(self.user)

        response = self.client.execute(self.keyword_query)

        expected = {
            "keywords": {
                "edges": [
                    {"node": {"tag": "first", "id": to_global_id("KeywordNode", 4)}},
                    {"node": {"tag": "test", "id": to_global_id("KeywordNode", 1)}},
                    {"node": {"tag": "test1", "id": to_global_id("KeywordNode", 2)}},
                    {"node": {"tag": "test2", "id": to_global_id("KeywordNode", 3)}},
                ]
            }
        }

        self.assertIsNone(response.errors)
        self.assertDictEqual(expected, response.data)
