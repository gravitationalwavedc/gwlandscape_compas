import humps
from django.contrib.auth import get_user_model
from django.test import override_settings
from graphql_relay import to_global_id

from compasui.tests.testcases import CompasTestCase
from publications.models import CompasPublication, Keyword
from publications.tests.test_utils import silence_errors

User = get_user_model()


class TestPublicationSchema(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(username="buffy", first_name="buffy", last_name="summers")

        self.keyword_ids = [
            Keyword.create_keyword('keyword1').id,
            Keyword.create_keyword('keyword2').id,
            Keyword.create_keyword('keyword3').id,
        ]

        self.keyword_global_ids = [to_global_id('KeywordNode', _id) for _id in self.keyword_ids]

        self.add_publication_mutation = """
            mutation AddPublicationMutation($input: AddPublicationMutationInput!) {
                addPublication(input: $input) {
                    id
                }
            }
        """

        self.delete_publication_mutation = """
            mutation DeletePublicationMutation($input: DeletePublicationMutationInput!) {
                deletePublication(input: $input) {
                    result
                }
            }
        """

        self.publication_input_required = {
            'input': {
                'author': 'test author',
                'title': 'test title',
                'arxivId': 'test arxiv_id'
            }
        }

        self.publication_input_full = {
            'input': {
                **self.publication_input_required['input'],
                'published': True,
                'year': 1983,
                'journal': 'test journal',
                'journalDoi': 'test journal doi',
                'datasetDoi': 'test dataset doi',
                'description': 'test description',
                'public': True,
                'downloadLink': 'test download link',
                'keywords': self.keyword_global_ids
            }
        }

        self.publication_query = """
            query {
                compasPublications {
                    edges {
                        node {
                            id
                            author
                            published
                            title
                            year
                            journal
                            journalDoi
                            datasetDoi
                            creationTime
                            description
                            public
                            downloadLink
                            arxivId
                            keywords {
                                edges {
                                    node {
                                        tag
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """

    def create_publication(self, **kwargs):
        inputs = {
            **humps.decamelize(self.publication_input_full['input']),
            'keywords': self.keyword_ids,
            **kwargs
        }
        return CompasPublication.create_publication(**inputs)

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_add_publication_authenticated(self):
        self.client.authenticate(self.user)

        response = self.client.execute(
            self.add_publication_mutation,
            self.publication_input_required
        )

        expected = {
            'addPublication': {
                'id': to_global_id('CompasPublication', 1)
            }
        }

        self.assertIsNone(response.errors)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(
            CompasPublication.objects.filter(**humps.decamelize(self.publication_input_required['input'])).count(),
            1
        )

        response = self.client.execute(
            self.add_publication_mutation,
            self.publication_input_full
        )

        expected = {
            'addPublication': {
                'id': to_global_id('CompasPublication', 2)
            }
        }

        self.assertIsNone(response.errors)
        self.assertDictEqual(expected, response.data)

        del self.publication_input_full['input']['keywords']

        for kw in Keyword.objects.all():
            self.assertEqual(
                CompasPublication.objects.filter(
                    **humps.decamelize(self.publication_input_full['input']),
                    keywords=kw
                ).count(),
                1
            )

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_add_publication_authenticated_not_publication_manager(self):
        self.client.authenticate(self.user)

        response = self.client.execute(
            self.add_publication_mutation,
            self.publication_input_required
        )

        expected = {
            'addPublication': None
        }

        self.assertEqual("You do not have permission to perform this action", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(
            CompasPublication.objects.filter(**humps.decamelize(self.publication_input_required['input'])).count(),
            0
        )

    @silence_errors
    def test_add_publication_unauthenticated(self):
        response = self.client.execute(
            self.add_publication_mutation,
            self.publication_input_required
        )

        expected = {
            'addPublication': None
        }

        self.assertEqual("You do not have permission to perform this action", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(
            CompasPublication.objects.filter(**humps.decamelize(self.publication_input_required['input'])).count(),
            0
        )

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_delete_publication_authenticated(self):
        self.client.authenticate(self.user)
        publication = self.create_publication()

        publication_input = {
            'input': {
                'id': to_global_id('Publication', publication.id),
            }
        }

        response = self.client.execute(
            self.delete_publication_mutation,
            publication_input
        )

        expected = {
            'deletePublication': {
                'result': True
            }
        }

        self.assertIsNone(response.errors)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(CompasPublication.objects.all().count(), 0)

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_delete_publication_authenticated_not_publication_manager(self):
        self.client.authenticate(self.user)
        publication = self.create_publication()

        publication_input = {
            'input': {
                'id': to_global_id('Publication', publication.id),
            }
        }

        response = self.client.execute(
            self.delete_publication_mutation,
            publication_input
        )

        expected = {
            'deletePublication': None
        }

        self.assertEqual("You do not have permission to perform this action", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(CompasPublication.objects.all().count(), 1)

    @silence_errors
    def test_delete_publication_unauthenticated(self):
        publication = self.create_publication()

        publication_input = {
            'input': {
                'id': to_global_id('Publication', publication.id),
            }
        }

        response = self.client.execute(
            self.delete_publication_mutation,
            publication_input
        )

        expected = {
            'deletePublication': None
        }

        self.assertEqual("You do not have permission to perform this action", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(CompasPublication.objects.all().count(), 1)

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_delete_publication_not_exists(self):
        self.client.authenticate(self.user)
        publication = self.create_publication()

        publication_input = {
            'input': {
                'id': to_global_id('Publication', publication.id + 1),
            }
        }

        response = self.client.execute(
            self.delete_publication_mutation,
            publication_input
        )

        expected = {
            'deletePublication': None
        }

        self.assertEqual("CompasPublication matching query does not exist.", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(CompasPublication.objects.all().count(), 1)

    def test_publication_query_unauthenticated(self):
        publication = self.create_publication()

        # publication = CompasPublication.create_publication(**humps.decamelize(self.publication_input_full['input']))

        response = self.client.execute(
            self.publication_query
        )

        expected = {
            'compasPublications': {
                'edges': [
                    {
                        'node': {
                            'id': 'Q29tcGFzUHVibGljYXRpb25Ob2RlOjE=',
                            'author': 'test author',
                            'published': True,
                            'title': 'test title',
                            'year': 1983,
                            'journal': 'test journal',
                            'journalDoi': 'test journal doi',
                            'datasetDoi': 'test dataset doi',
                            'creationTime': publication.creation_time.isoformat(),
                            'description': 'test description',
                            'public': True,
                            'downloadLink': 'test download link',
                            'arxivId': 'test arxiv_id',
                            'keywords': {
                                'edges': [
                                    {
                                        'node': {
                                            'tag': 'keyword1'
                                        }
                                    },
                                    {
                                        'node': {
                                            'tag': 'keyword2'
                                        }
                                    },
                                    {
                                        'node': {
                                            'tag': 'keyword3'
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        }

        self.assertIsNone(response.errors)
        self.assertDictEqual(expected, response.data)

    def test_publication_query_authenticated(self):
        self.client.authenticate(self.user)
        publication = self.create_publication()

        response = self.client.execute(
            self.publication_query
        )

        expected = {
            'compasPublications': {
                'edges': [
                    {
                        'node': {
                            'id': 'Q29tcGFzUHVibGljYXRpb25Ob2RlOjE=',
                            'author': 'test author',
                            'published': True,
                            'title': 'test title',
                            'year': 1983,
                            'journal': 'test journal',
                            'journalDoi': 'test journal doi',
                            'datasetDoi': 'test dataset doi',
                            'creationTime': publication.creation_time.isoformat(),
                            'description': 'test description',
                            'public': True,
                            'downloadLink': 'test download link',
                            'arxivId': 'test arxiv_id',
                            'keywords': {
                                'edges': [
                                    {
                                        'node': {
                                            'tag': 'keyword1'
                                        }
                                    },
                                    {
                                        'node': {
                                            'tag': 'keyword2'
                                        }
                                    },
                                    {
                                        'node': {
                                            'tag': 'keyword3'
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        }

        self.assertIsNone(response.errors)
        self.assertDictEqual(expected, response.data)

    def test_publication_query_filter_public_unauthenticated(self):
        publication = self.create_publication()

        # Add another publication with public=False - this should not show up in the output of the query for an
        # anonymous query
        self.create_publication(public=False)

        response = self.client.execute(
            self.publication_query
        )

        expected = {
            'compasPublications': {
                'edges': [
                    {
                        'node': {
                            'id': 'Q29tcGFzUHVibGljYXRpb25Ob2RlOjE=',
                            'author': 'test author',
                            'published': True,
                            'title': 'test title',
                            'year': 1983,
                            'journal': 'test journal',
                            'journalDoi': 'test journal doi',
                            'datasetDoi': 'test dataset doi',
                            'creationTime': publication.creation_time.isoformat(),
                            'description': 'test description',
                            'public': True,
                            'downloadLink': 'test download link',
                            'arxivId': 'test arxiv_id',
                            'keywords': {
                                'edges': [
                                    {
                                        'node': {
                                            'tag': 'keyword1'
                                        }
                                    },
                                    {
                                        'node': {
                                            'tag': 'keyword2'
                                        }
                                    },
                                    {
                                        'node': {
                                            'tag': 'keyword3'
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        }

        self.assertIsNone(response.errors)
        self.assertDictEqual(expected, response.data)

    def test_publication_query_filter_public_authenticated(self):
        self.client.authenticate(self.user)
        publication = self.create_publication()

        # Add another publication with public=False - this should not show up in the output of the query for an
        # authenticated user who is not a publication manager
        self.create_publication(public=False)

        response = self.client.execute(
            self.publication_query
        )

        expected = {
            'compasPublications': {
                'edges': [
                    {
                        'node': {
                            'id': 'Q29tcGFzUHVibGljYXRpb25Ob2RlOjE=',
                            'author': 'test author',
                            'published': True,
                            'title': 'test title',
                            'year': 1983,
                            'journal': 'test journal',
                            'journalDoi': 'test journal doi',
                            'datasetDoi': 'test dataset doi',
                            'creationTime': publication.creation_time.isoformat(),
                            'description': 'test description',
                            'public': True,
                            'downloadLink': 'test download link',
                            'arxivId': 'test arxiv_id',
                            'keywords': {
                                'edges': [
                                    {
                                        'node': {
                                            'tag': 'keyword1'
                                        }
                                    },
                                    {
                                        'node': {
                                            'tag': 'keyword2'
                                        }
                                    },
                                    {
                                        'node': {
                                            'tag': 'keyword3'
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        }

        self.assertIsNone(response.errors)
        self.assertDictEqual(expected, response.data)

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_publication_query_filter_public_authenticated_publication_manager(self):
        self.client.authenticate(self.user)
        publication = self.create_publication()

        # Add another publication with public=False - this should show up in the output of the query for a publication
        # manager
        publication2 = self.create_publication(public=False)

        response = self.client.execute(
            self.publication_query
        )

        expected = {
            'compasPublications': {
                'edges': [
                    {
                        'node': {
                            'id': 'Q29tcGFzUHVibGljYXRpb25Ob2RlOjE=',
                            'author': 'test author',
                            'published': True,
                            'title': 'test title',
                            'year': 1983,
                            'journal': 'test journal',
                            'journalDoi': 'test journal doi',
                            'datasetDoi': 'test dataset doi',
                            'creationTime': publication.creation_time.isoformat(),
                            'description': 'test description',
                            'public': True,
                            'downloadLink': 'test download link',
                            'arxivId': 'test arxiv_id',
                            'keywords': {
                                'edges': [
                                    {
                                        'node': {
                                            'tag': 'keyword1'
                                        }
                                    },
                                    {
                                        'node': {
                                            'tag': 'keyword2'
                                        }
                                    },
                                    {
                                        'node': {
                                            'tag': 'keyword3'
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    {
                        'node': {
                            'arxivId': 'test arxiv_id',
                            'author': 'test author',
                            'creationTime': publication2.creation_time.isoformat(),
                            'datasetDoi': 'test dataset doi',
                            'description': 'test description',
                            'public': False,
                            'downloadLink': 'test download link',
                            'id': 'Q29tcGFzUHVibGljYXRpb25Ob2RlOjI=',
                            'journal': 'test journal',
                            'journalDoi': 'test journal doi',
                            'keywords': {
                                'edges': [
                                    {
                                        'node': {
                                            'tag': 'keyword1'
                                        }
                                    },
                                    {
                                        'node': {
                                            'tag': 'keyword2'
                                        }
                                    },
                                    {
                                        'node': {
                                            'tag': 'keyword3'
                                        }
                                    }
                                ]
                            },
                            'published': True,
                            'title': 'test title',
                            'year': 1983
                        }
                    }
                ]
            }
        }

        self.assertIsNone(response.errors)
        self.assertDictEqual(expected, response.data)
