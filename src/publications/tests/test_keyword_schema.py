from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import override_settings
from graphql_relay import to_global_id

from compasui.tests.testcases import CompasTestCase
from publications.models import Keyword

User = get_user_model()


class TestKeywordSchema(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(username="buffy", first_name="buffy", last_name="summers")

        self.add_keyword_mutation = """
            mutation AddKeywordMutation($input: AddKeywordMutationInput!) {
                addKeyword(input: $input) {
                    id
                }
            }
        """

        self.delete_keyword_mutation = """
            mutation DeleteKeywordMutation($input: DeleteKeywordMutationInput!) {
                deleteKeyword(input: $input) {
                    result
                }
            }
        """

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

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_add_keyword_authenticated(self):
        self.client.authenticate(self.user)

        keyword_input = {
            'input': {
                'tag': 'test'
            }
        }

        response = self.client.execute(
            self.add_keyword_mutation,
            keyword_input
        )

        expected = {
            'addKeyword': {
                'id': to_global_id('Keyword', Keyword.objects.last().id),
            }
        }

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(Keyword.objects.filter(tag=keyword_input['input']['tag']).count(), 1)

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_add_keyword_authenticated_not_publication_manager(self):
        self.client.authenticate(self.user)

        keyword_input = {
            'input': {
                'tag': 'test'
            }
        }

        response = self.client.execute(
            self.add_keyword_mutation,
            keyword_input
        )

        expected = {
            'addKeyword': None
        }

        self.assertEqual("You do not have permission to perform this action", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(Keyword.objects.filter(tag=keyword_input['input']['tag']).count(), 0)

    def test_add_keyword_unauthenticated(self):
        keyword_input = {
            'input': {
                'tag': 'test'
            }
        }

        response = self.client.execute(
            self.add_keyword_mutation,
            keyword_input
        )

        expected = {
            'addKeyword': None
        }

        self.assertEqual("You do not have permission to perform this action", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(Keyword.objects.filter(tag=keyword_input['input']['tag']).count(), 0)

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_add_keyword_duplicate_tag(self):
        self.client.authenticate(self.user)

        keyword_input = {
            'input': {
                'tag': 'test'
            }
        }

        self.client.execute(
            self.add_keyword_mutation,
            keyword_input
        )

        with transaction.atomic():
            response = self.client.execute(
                self.add_keyword_mutation,
                keyword_input
            )

        expected = {
            'addKeyword': None
        }

        self.assertEqual("UNIQUE constraint failed: publications_keyword.tag", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(Keyword.objects.filter(tag=keyword_input['input']['tag']).count(), 1)

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_delete_keyword_authenticated(self):
        self.client.authenticate(self.user)

        kw = Keyword.create_keyword('test')

        keyword_input = {
            'input': {
                'id': to_global_id('Keyword', kw.id),
            }
        }

        response = self.client.execute(
            self.delete_keyword_mutation,
            keyword_input
        )

        expected = {
            'deleteKeyword': {
                'result': True
            }
        }

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(Keyword.objects.all().count(), 0)

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_delete_keyword_authenticated_not_publication_manager(self):
        self.client.authenticate(self.user)

        kw = Keyword.create_keyword('test')

        keyword_input = {
            'input': {
                'id': to_global_id('Keyword', kw.id),
            }
        }

        response = self.client.execute(
            self.delete_keyword_mutation,
            keyword_input
        )

        expected = {
            'deleteKeyword': None
        }

        self.assertEqual("You do not have permission to perform this action", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(Keyword.objects.all().count(), 1)

    def test_delete_keyword_unauthenticated(self):
        kw = Keyword.create_keyword('test')

        keyword_input = {
            'input': {
                'id': to_global_id('Keyword', kw.id),
            }
        }

        response = self.client.execute(
            self.delete_keyword_mutation,
            keyword_input
        )

        expected = {
            'deleteKeyword': None
        }

        self.assertEqual("You do not have permission to perform this action", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(Keyword.objects.all().count(), 1)

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_delete_keyword_not_exists(self):
        self.client.authenticate(self.user)

        kw = Keyword.create_keyword('test')

        keyword_input = {
            'input': {
                'id': to_global_id('Keyword', kw.id+1),
            }
        }

        response = self.client.execute(
            self.delete_keyword_mutation,
            keyword_input
        )

        expected = {
            'deleteKeyword': None
        }

        self.assertEqual("Keyword matching query does not exist.", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(Keyword.objects.all().count(), 1)

    def test_keyword_query_unauthenticated(self):
        Keyword.create_keyword('test')
        Keyword.create_keyword('test1')
        Keyword.create_keyword('test2')
        Keyword.create_keyword('first')

        response = self.client.execute(
            self.keyword_query
        )

        expected = {
            'keywords': {
                'edges': [
                    {'node': {'tag': 'first', 'id': to_global_id('KeywordNode', 4)}},
                    {'node': {'tag': 'test', 'id': to_global_id('KeywordNode', 1)}},
                    {'node': {'tag': 'test1', 'id': to_global_id('KeywordNode', 2)}},
                    {'node': {'tag': 'test2', 'id': to_global_id('KeywordNode', 3)}}
                ]
            }
        }

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)

    def test_keyword_query_authenticated(self):
        self.client.authenticate(self.user)

        Keyword.create_keyword('test')
        Keyword.create_keyword('test1')
        Keyword.create_keyword('test2')
        Keyword.create_keyword('first')

        response = self.client.execute(
            self.keyword_query
        )

        expected = {
            'keywords': {
                'edges': [
                    {'node': {'tag': 'first', 'id': to_global_id('KeywordNode', 4)}},
                    {'node': {'tag': 'test', 'id': to_global_id('KeywordNode', 1)}},
                    {'node': {'tag': 'test1', 'id': to_global_id('KeywordNode', 2)}},
                    {'node': {'tag': 'test2', 'id': to_global_id('KeywordNode', 3)}}
                ]
            }
        }

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)
