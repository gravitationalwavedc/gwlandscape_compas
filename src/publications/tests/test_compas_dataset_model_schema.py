import pathlib
import uuid
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from graphql_relay import to_global_id

from compasui.tests.testcases import CompasTestCase
from publications.models import (
    CompasPublication,
    CompasModel,
    CompasDatasetModel,
    Upload,
    Keyword,
)
from publications.tests.test_utils import silence_errors

User = get_user_model()


def create_model_publication(i=1):
    model = CompasModel.create_model(f"test {i}", "summary", "description")

    keywords = [
        Keyword.create_keyword(f"keyword1{i}"),
        Keyword.create_keyword(f"keyword2{i}"),
        Keyword.create_keyword(f"keyword3{i}"),
    ]

    publication = CompasPublication.create_publication(
        author=f"test author {i}",
        title=f"test title {i}",
        arxiv_id=f"test arxiv_id {i}",
    )

    publication.keywords.set(keywords)

    return model, publication


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
class TestUploadCompasDatasetModelSchema(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="buffy", first_name="buffy", last_name="summers"
        )

        self.model, self.publication = create_model_publication()

        self.generate_compas_dataset_model_upload_token_query = """
            query {
                generateCompasDatasetModelUploadToken {
                    token
                }
            }
        """

        self.upload_compas_dataset_model_mutation = """
            mutation UploadCompasDatasetModelMutation($input: UploadCompasDatasetModelMutationInput!) {
                uploadCompasDatasetModel(input: $input) {
                    id
                }
            }
        """

        self.archive_input = {
            "input": {
                "compasPublication": to_global_id(
                    "CompasPublication", self.publication.id
                ),
                "compasModel": to_global_id("CompasModel", self.model.id),
                "jobFile": SimpleUploadedFile(
                    name="test.tar.gz",
                    content=open(
                        "./publications/tests/test_data/test_job.tar.gz", "rb"
                    ).read(),
                    content_type="application/gzip",
                ),
            }
        }

        self.single_input = {
            "input": {
                "compasPublication": to_global_id(
                    "CompasPublication", self.publication.id
                ),
                "compasModel": to_global_id("CompasModel", self.model.id),
                "jobFile": SimpleUploadedFile(
                    name="COMPAS_Output.h5",
                    content=open(
                        "./publications/tests/test_data/test_job/COMPAS_Output/COMPAS_Output.h5",
                        "rb",
                    ).read(),
                    content_type="application/x-bag",
                ),
            }
        }

        self.expected_output = {
            "uploadCompasDatasetModel": {
                "id": to_global_id("CompasDatasetModelNode", 1),
            }
        }

        self.null_output = {"generateCompasDatasetModelUploadToken": None}

    def execute_token_query(self):
        return self.client.execute(
            self.generate_compas_dataset_model_upload_token_query
        )

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_upload_compas_dataset_model_authenticated_archive(self):
        self.client.authenticate(self.user)

        response = self.execute_token_query()
        self.archive_input["input"]["uploadToken"] = response.data[
            "generateCompasDatasetModelUploadToken"
        ]["token"]

        response = self.client.execute(
            self.upload_compas_dataset_model_mutation, self.archive_input
        )

        self.assertIsNone(response.errors)
        self.assertDictEqual(self.expected_output, response.data)

        self.assertEqual(
            CompasDatasetModel.objects.filter(
                compas_publication=self.publication, compas_model=self.model
            ).count(),
            1,
        )

        files = ["COMPAS_Output.h5", "Run_Details", "BSE_grid.txt"]

        self.assertEqual(3, Upload.objects.all().count())
        for f in files:
            self.assertTrue(
                Upload.objects.filter(
                    file__contains=f, dataset_model=CompasDatasetModel.objects.last()
                ).exists()
            )

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_upload_compas_dataset_model_authenticated_single(self):
        # Test that a user who is in PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS can create a dataset model for a single
        # file
        self.client.authenticate(self.user)

        response = self.execute_token_query()
        self.single_input["input"]["uploadToken"] = response.data[
            "generateCompasDatasetModelUploadToken"
        ]["token"]

        response = self.client.execute(
            self.upload_compas_dataset_model_mutation, self.single_input
        )

        self.assertIsNone(response.errors)
        self.assertDictEqual(self.expected_output, response.data)

        self.assertEqual(
            CompasDatasetModel.objects.filter(
                compas_publication=self.publication, compas_model=self.model
            ).count(),
            1,
        )

        self.assertEqual(Upload.objects.all().count(), 1)
        self.assertEqual(
            Upload.objects.last().file.name, "publications/1/1/COMPAS_Output.h5"
        )

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_upload_compas_dataset_model_authenticated_not_publication_manager(self):
        # Shouldn't be able to create a dataset model upload token if a user isn't in
        # PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS
        self.client.authenticate(self.user)

        response = self.execute_token_query()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertEqual(
            CompasDatasetModel.objects.filter(
                compas_publication=self.publication, compas_model=self.model
            ).count(),
            0,
        )

    @silence_errors
    def test_generate_compas_dataset_model_upload_token_unauthenticated(self):
        response = self.execute_token_query()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertEqual(
            CompasDatasetModel.objects.filter(
                compas_publication=self.publication, compas_model=self.model
            ).count(),
            0,
        )

    @silence_errors
    def test_upload_compas_dataset_model_upload_token(self):
        # Verify that illegal tokens are not accepted
        self.single_input["input"]["uploadToken"] = str(uuid.uuid4())

        response = self.client.execute(
            self.upload_compas_dataset_model_mutation, self.single_input
        )

        expected = {"uploadCompasDatasetModel": None}

        self.assertEqual(
            "Compas Dataset Model upload token is invalid or expired.",
            response.errors[0].message,
        )
        self.assertDictEqual(expected, response.data)


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
class TestDeleteCompasDatasetModelSchema(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="buffy", first_name="buffy", last_name="summers"
        )

        self.model, self.publication = create_model_publication()

        self.delete_compas_dataset_model_mutation = """
            mutation DeleteCompasDatasetModelMutation($input: DeleteCompasDatasetModelMutationInput!) {
                deleteCompasDatasetModel(input: $input) {
                    result
                }
            }
        """

        self.dataset_model = CompasDatasetModel.create_dataset_model(
            self.publication,
            self.model,
            SimpleUploadedFile(
                name="test.tar.gz",
                content=open(
                    "./publications/tests/test_data/test_job.tar.gz", "rb"
                ).read(),
                content_type="application/gzip",
            ),
        )

        self.dataset_model_input = {
            "input": {
                "id": to_global_id("CompasDatasetModelNode", self.dataset_model.id),
            }
        }

        self.null_output = {"deleteCompasDatasetModel": None}

    def execute_query(self):
        return self.client.execute(
            self.delete_compas_dataset_model_mutation, self.dataset_model_input
        )

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_delete_compas_dataset_model_authenticated(self):
        self.client.authenticate(self.user)

        file = self.dataset_model.upload_set.first().file.path
        self.assertTrue(pathlib.Path(file).exists())

        response = self.execute_query()

        expected = {"deleteCompasDatasetModel": {"result": True}}

        self.assertIsNone(response.errors)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(CompasDatasetModel.objects.all().count(), 0)
        self.assertEqual(Upload.objects.all().count(), 0)

        # The Uploaded files should be deleted
        self.assertFalse(pathlib.Path(file).exists())

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_delete_compas_dataset_model_authenticated_not_publication_manager(self):
        self.client.authenticate(self.user)

        response = self.execute_query()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertEqual(CompasDatasetModel.objects.all().count(), 1)
        self.assertEqual(Upload.objects.all().count(), 3)

    @silence_errors
    def test_delete_compas_dataset_model_unauthenticated(self):
        response = self.execute_query()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertEqual(CompasDatasetModel.objects.all().count(), 1)
        self.assertEqual(Upload.objects.all().count(), 3)

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_delete_compas_dataset_model_not_exists(self):
        self.client.authenticate(self.user)

        self.dataset_model_input["input"]["id"] = to_global_id(
            "CompasDatasetModelNode", self.dataset_model.id + 1
        )
        response = self.execute_query()

        self.assertEqual(
            "CompasDatasetModel matching query does not exist.",
            response.errors[0].message,
        )
        self.assertDictEqual(self.null_output, response.data)

        self.assertEqual(CompasPublication.objects.all().count(), 1)


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
class TestUpdateteCompasDatasetModelSchema(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="buffy", first_name="buffy", last_name="summers"
        )

        self.model1, self.publication1 = create_model_publication(i=1)
        self.model2, self.publication2 = create_model_publication(i=2)

        self.update_compas_dataset_model_mutation = """
            mutation UpdateCompasDatasetModelMutation($input: UpdateCompasDatasetModelMutationInput!) {
                updateCompasDatasetModel(input: $input) {
                    result
                }
            }
        """

        self.dataset_model = CompasDatasetModel.create_dataset_model(
            self.publication1,
            self.model1,
            SimpleUploadedFile(
                name="test.tar.gz",
                content=open(
                    "./publications/tests/test_data/test_job.tar.gz", "rb"
                ).read(),
                content_type="application/gzip",
            ),
        )

        self.dataset_model_input = {
            "input": {
                "id": to_global_id("CompasDatasetModelNode", self.dataset_model.id),
                "compasPublication": to_global_id(
                    "CompasPublicationNode", self.publication2.id
                ),
                "compasModel": to_global_id("CompasModelNode", self.model2.id),
            }
        }

        self.null_output = {"updateCompasDatasetModel": None}

    def execute_query(self):
        return self.client.execute(
            self.update_compas_dataset_model_mutation, self.dataset_model_input
        )

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_update_compas_dataset_model_authenticated(self):
        self.client.authenticate(self.user)

        response = self.execute_query()

        expected = {"updateCompasDatasetModel": {"result": True}}

        self.assertIsNone(response.errors)
        self.assertDictEqual(expected, response.data)

        self.dataset_model.refresh_from_db()

        self.assertEqual(self.dataset_model.compas_publication, self.publication2)
        self.assertEqual(self.dataset_model.compas_model, self.model2)

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_update_compas_dataset_model_authenticated_not_publication_manager(self):
        self.client.authenticate(self.user)

        response = self.execute_query()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(self.null_output, response.data)

        self.dataset_model.refresh_from_db()

        self.assertEqual(self.dataset_model.compas_publication, self.publication1)
        self.assertEqual(self.dataset_model.compas_model, self.model1)

    @silence_errors
    def test_update_compas_dataset_model_unauthenticated(self):
        response = self.execute_query()

        self.assertEqual(
            "You do not have permission to perform this action",
            response.errors[0].message,
        )
        self.assertDictEqual(self.null_output, response.data)

        self.dataset_model.refresh_from_db()

        self.assertEqual(self.dataset_model.compas_publication, self.publication1)
        self.assertEqual(self.dataset_model.compas_model, self.model1)

    @silence_errors
    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_update_compas_dataset_model_not_exists(self):
        self.client.authenticate(self.user)

        self.dataset_model_input["input"]["id"] = to_global_id(
            "CompasDatasetModelNode", self.dataset_model.id + 1
        )
        response = self.execute_query()

        self.assertEqual(
            "CompasDatasetModel matching query does not exist.",
            response.errors[0].message,
        )
        self.assertDictEqual(self.null_output, response.data)

        self.dataset_model.refresh_from_db()

        self.assertEqual(self.dataset_model.compas_publication, self.publication1)
        self.assertEqual(self.dataset_model.compas_model, self.model1)


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
class TestQueryCompasDatasetModelSchema(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="buffy", first_name="buffy", last_name="summers"
        )

        self.model, self.publication = create_model_publication()

        self.publication.public = True
        self.publication.save()

        self.dataset_model_query = """
            query {
                compasDatasetModels {
                    edges {
                        node {
                            id
                            compasPublication {
                                id
                                author
                                title
                                arxivId
                                keywords {
                                    edges {
                                        node {
                                            tag
                                        }
                                    }
                                }
                            }
                            compasModel {
                                id
                                name
                                summary
                                description
                            }
                            files {
                                path
                            }
                        }
                    }
                }
            }
        """

        self.dataset_model = CompasDatasetModel.create_dataset_model(
            self.publication,
            self.model,
            SimpleUploadedFile(
                name="test.tar.gz",
                content=open(
                    "./publications/tests/test_data/test_job.tar.gz", "rb"
                ).read(),
                content_type="application/gzip",
            ),
        )

        self.expected_output = {
            "compasDatasetModels": {
                "edges": [
                    {
                        "node": {
                            "id": "Q29tcGFzRGF0YXNldE1vZGVsTm9kZTox",
                            "compasPublication": {
                                "id": "Q29tcGFzUHVibGljYXRpb25Ob2RlOjE=",
                                "author": "test author 1",
                                "title": "test title 1",
                                "arxivId": "test arxiv_id 1",
                                "keywords": {
                                    "edges": [
                                        {"node": {"tag": "keyword11"}},
                                        {"node": {"tag": "keyword21"}},
                                        {"node": {"tag": "keyword31"}},
                                    ]
                                },
                            },
                            "compasModel": {
                                "id": "Q29tcGFzTW9kZWxOb2RlOjE=",
                                "name": "test 1",
                                "summary": "summary",
                                "description": "description",
                            },
                            "files": [
                                {"path": "test_job/COMPAS_Output/COMPAS_Output.h5"},
                                {"path": "test_job/COMPAS_Output/Run_Details"},
                                {"path": "test_job/BSE_grid.txt"},
                            ],
                        }
                    }
                ]
            }
        }

    def execute_query(self):
        return self.client.execute(self.dataset_model_query)

    def test_compas_dataset_model_query_unauthenticated(self):
        response = self.execute_query()

        self.assertIsNone(response.errors)
        self.assertDictEqual(self.expected_output, response.data)

    def test_compas_dataset_model_query_authenticated(self):
        self.client.authenticate(self.user)

        response = self.execute_query()

        self.assertIsNone(response.errors)
        self.assertDictEqual(self.expected_output, response.data)
