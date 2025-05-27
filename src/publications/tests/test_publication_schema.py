import humps
from django.contrib.auth import get_user_model
from django.test import override_settings
from graphql_relay import to_global_id

from compasui.tests.testcases import CompasTestCase
from publications.models import CompasPublication, Keyword
from publications.tests.test_utils import silence_errors

User = get_user_model()


def create_keywords():
    Keyword.create_keyword("keyword1")
    Keyword.create_keyword("keyword2")
    Keyword.create_keyword("keyword3")


def create_publication(**kwargs):
    inputs = {
        "author": "test author",
        "title": "test title",
        "arxiv_id": "test arxiv_id",
        "published": True,
        "year": 1983,
        "journal": "test journal",
        "journal_doi": "test journal doi",
        "dataset_doi": "test dataset doi",
        "description": "test description",
        "public": True,
        "download_link": "test download link",
        "keywords": list(Keyword.objects.all().values_list("id", flat=True)),
        **kwargs,
    }
    return CompasPublication.create_publication(**inputs)


class TestAddPublicationSchema(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="buffy", first_name="buffy", last_name="summers"
        )

        create_keywords()
        self.keyword_global_ids = [
            to_global_id("KeywordNode", _id)
            for _id in list(Keyword.objects.all().values_list("id", flat=True))
        ]

        self.add_publication_mutation = """
            mutation AddPublicationMutation($input: AddPublicationMutationInput!) {
                addPublication(input: $input) {
                    id
                }
            }
        """

        self.publication_input_required = {
            "input": {
                "author": "test author",
                "title": "test title",
                "arxivId": "test arxiv_id",
            }
        }

        self.publication_input_full = {
            "input": {
                **self.publication_input_required["input"],
                "published": True,
                "year": 1983,
                "journal": "test journal",
                "journalDoi": "test journal doi",
                "datasetDoi": "test dataset doi",
                "description": "test description",
                "public": True,
                "downloadLink": "test download link",
                "keywords": self.keyword_global_ids,
            }
        }

        self.expected_output = {
            "addPublication": {"id": to_global_id("CompasPublicationNode", 1)}
        }

        self.null_output = {"addPublication": None}

    def execute_query(self):
        return self.query(
            self.add_publication_mutation, input_data=self.publication_input_required["input"]
        )

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_add_publication_authenticated(self):
        self.client.authenticate(self.user)

        response = self.execute_query()

        self.assertIsNone(response.errors)
        self.assertDictEqual(self.expected_output, response.data)

        self.assertEqual(
            CompasPublication.objects.filter(
                **humps.decamelize(self.publication_input_required["input"])
            ).count(),
            1,
        )

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_add_full_publication_authenticated(self):
        self.client.authenticate(self.user)

        response = self.query(
            self.add_publication_mutation, input_data=self.publication_input_full["input"]
        )

        self.assertIsNone(response.errors)
        self.assertDictEqual(self.expected_output, response.data)

        self.assertEqual(
            CompasPublication.objects.filter(
                **humps.decamelize(self.publication_input_required["input"])
            ).count(),
            1,
        )

        del self.publication_input_full["input"]["keywords"]

        for kw in Keyword.objects.all():
            self.assertEqual(
                CompasPublication.objects.filter(
                    **humps.decamelize(self.publication_input_full["input"]),
                    keywords=kw
                ).count(),
                1,
            )

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_add_publication_authenticated_not_publication_manager(self):
        self.client.authenticate(self.user)

        response = self.execute_query()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertEqual(
            CompasPublication.objects.filter(
                **humps.decamelize(self.publication_input_required["input"])
            ).count(),
            0,
        )

    @silence_errors
    def test_add_publication_unauthenticated(self):
        response = self.execute_query()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertEqual(
            CompasPublication.objects.filter(
                **humps.decamelize(self.publication_input_required["input"])
            ).count(),
            0,
        )


class TestDeletePublicationSchema(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="buffy", first_name="buffy", last_name="summers"
        )

        self.delete_publication_mutation = """
            mutation DeletePublicationMutation($input: DeletePublicationMutationInput!) {
                deletePublication(input: $input) {
                    result
                }
            }
        """

        create_keywords()
        self.publication = create_publication()
        self.publication_input = {
            "input": {
                "id": to_global_id("CompasPublicationNode", self.publication.id),
            }
        }

        self.expected_output = {"deletePublication": {"result": True}}

        self.null_output = {"deletePublication": None}

    def execute_query(self):
        return self.query(
            self.delete_publication_mutation, input_data=self.publication_input["input"]
        )

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_delete_publication_authenticated(self):
        self.client.authenticate(self.user)

        response = self.execute_query()

        self.assertIsNone(response.errors)
        self.assertDictEqual(self.expected_output, response.data)

        self.assertEqual(CompasPublication.objects.all().count(), 0)

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_delete_publication_authenticated_not_publication_manager(self):
        self.client.authenticate(self.user)

        response = self.execute_query()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertEqual(CompasPublication.objects.all().count(), 1)

    @silence_errors
    def test_delete_publication_unauthenticated(self):
        response = self.execute_query()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertEqual(CompasPublication.objects.all().count(), 1)

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_delete_publication_not_exists(self):
        self.client.authenticate(self.user)

        self.publication_input["input"]["id"] = to_global_id(
            "CompasPublicationNode", self.publication.id + 1
        )
        response = self.execute_query()

        self.assertEqual(
            "CompasPublication matching query does not exist.",
            response.errors[0].message,
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertEqual(CompasPublication.objects.all().count(), 1)


class TestUpdatePublicationSchema(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="buffy", first_name="buffy", last_name="summers"
        )

        self.update_publication_mutation = """
            mutation UpdatePublicationMutation($input: UpdatePublicationMutationInput!) {
                updatePublication(input: $input) {
                    result
                }
            }
        """

        create_keywords()
        self.publication = create_publication()

        self.initial_publication_fields = self.get_publication_fields(self.publication)
        self.updated_publication_fields = {
            "author": "new test author",
            "title": "new test title",
            "description": "new test description",
            "arxiv_id": "new test arxiv_id",
            "published": False,
            "year": 1984,
            "journal": "new test journal",
            "journal_doi": "new test journal doi",
            "dataset_doi": "new test dataset doi",
            "public": False,
            "download_link": "new test download link",
            "keywords": [Keyword.objects.first().id],
        }
        self.publication_input = {
            "input": {
                "id": to_global_id("CompasPublicationNode", self.publication.id),
                **humps.camelize(self.updated_publication_fields),
            }
        }
        self.publication_input["input"]["keywords"] = [
            to_global_id("KeywordNode", Keyword.objects.first().id)
        ]

        self.expected_output = {"updatePublication": {"result": True}}

        self.null_output = {"updatePublication": None}

    def get_publication_fields(self, publication):
        vals = {
            field: getattr(self.publication, field)
            for field in [
                "author",
                "title",
                "description",
                "arxiv_id",
                "published",
                "year",
                "journal",
                "journal_doi",
                "dataset_doi",
                "public",
                "download_link",
            ]
        }
        vals["keywords"] = list(self.publication.keywords.values_list("id", flat=True))
        return vals

    def execute_query(self):
        return self.query(
            self.update_publication_mutation, input_data=self.publication_input["input"]
        )

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_update_publication_authenticated(self):
        self.client.authenticate(self.user)

        response = self.execute_query()
        self.publication.refresh_from_db()

        self.assertIsNone(response.errors)
        self.assertDictEqual(self.expected_output, response.data)

        self.assertDictEqual(
            self.get_publication_fields(self.publication),
            self.updated_publication_fields,
        )

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_update_publication_authenticated_not_publication_manager(self):
        self.client.authenticate(self.user)

        response = self.execute_query()
        self.publication.refresh_from_db()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertDictEqual(
            self.get_publication_fields(self.publication),
            self.initial_publication_fields,
        )

    @silence_errors
    def test_update_publication_unauthenticated(self):
        response = self.execute_query()
        self.publication.refresh_from_db()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertDictEqual(
            self.get_publication_fields(self.publication),
            self.initial_publication_fields,
        )

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_update_publication_not_exists(self):
        self.client.authenticate(self.user)

        self.publication_input["input"]["id"] = to_global_id(
            "CompasPublicationNode", self.publication.id + 1
        )
        response = self.execute_query()
        self.publication.refresh_from_db()

        self.assertEqual(
            "CompasPublication matching query does not exist.",
            response.errors[0].message,
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertDictEqual(
            self.get_publication_fields(self.publication),
            self.initial_publication_fields,
        )


class TestQueryPublicationSchema(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="buffy", first_name="buffy", last_name="summers"
        )

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

        create_keywords()
        self.publication = create_publication()
        # Add another publication with public=False - this should not show up in the output of the query for an
        # anonymous query, or for anyone who is not a publication manager
        self.private_publication = create_publication(public=False)

        self.expected_output = {
            "compasPublications": {
                "edges": [
                    {
                        "node": {
                            "id": to_global_id(
                                "CompasPublicationNode", self.publication.id
                            ),
                            "author": "test author",
                            "published": True,
                            "title": "test title",
                            "year": 1983,
                            "journal": "test journal",
                            "journalDoi": "test journal doi",
                            "datasetDoi": "test dataset doi",
                            "creationTime": self.publication.creation_time.isoformat(),
                            "description": "test description",
                            "public": True,
                            "downloadLink": "test download link",
                            "arxivId": "test arxiv_id",
                            "keywords": {
                                "edges": [
                                    {"node": {"tag": "keyword1"}},
                                    {"node": {"tag": "keyword2"}},
                                    {"node": {"tag": "keyword3"}},
                                ]
                            },
                        }
                    }
                ]
            }
        }

    def execute_query(self):
        return self.query(self.publication_query)

    def test_publication_query_unauthenticated(self):
        response = self.execute_query()

        self.assertIsNone(response.errors)
        self.assertDictEqual(self.expected_output, response.data)

    def test_publication_query_authenticated(self):
        self.client.authenticate(self.user)

        response = self.execute_query()

        self.assertIsNone(response.errors)
        self.assertDictEqual(self.expected_output, response.data)

    def test_publication_query_filter_public_unauthenticated(self):
        response = self.execute_query()

        self.assertIsNone(response.errors)
        self.assertDictEqual(self.expected_output, response.data)

    def test_publication_query_filter_public_authenticated(self):
        self.client.authenticate(self.user)

        response = self.execute_query()

        self.assertIsNone(response.errors)
        self.assertDictEqual(self.expected_output, response.data)

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_publication_query_filter_public_authenticated_publication_manager(self):
        self.client.authenticate(self.user)

        response = self.execute_query()

        self.expected_output["compasPublications"]["edges"].append(
            {
                "node": {
                    "id": to_global_id(
                        "CompasPublicationNode", self.private_publication.id
                    ),
                    "arxivId": "test arxiv_id",
                    "author": "test author",
                    "creationTime": self.private_publication.creation_time.isoformat(),
                    "datasetDoi": "test dataset doi",
                    "description": "test description",
                    "public": False,
                    "downloadLink": "test download link",
                    "journal": "test journal",
                    "journalDoi": "test journal doi",
                    "keywords": {
                        "edges": [
                            {"node": {"tag": "keyword1"}},
                            {"node": {"tag": "keyword2"}},
                            {"node": {"tag": "keyword3"}},
                        ]
                    },
                    "published": True,
                    "title": "test title",
                    "year": 1983,
                }
            }
        )

        self.assertIsNone(response.errors)
        self.assertDictEqual(self.expected_output, response.data)
