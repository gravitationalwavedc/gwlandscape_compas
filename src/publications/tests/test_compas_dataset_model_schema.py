from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from graphql_relay import to_global_id

from compasui.tests.testcases import CompasTestCase
from publications.models import CompasPublication, CompasModel, CompasDatasetModel, Upload, Keyword

User = get_user_model()


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
class TestCompasDatasetModelSchema(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(username="buffy", first_name="buffy", last_name="summers")

        self.model = CompasModel.create_model('test', 'summary', 'description')

        self.keywords = [
            Keyword.create_keyword('keyword1'),
            Keyword.create_keyword('keyword2'),
            Keyword.create_keyword('keyword3')
        ]

        self.publication = CompasPublication.create_publication(
            author='test author',
            title='test title',
            arxiv_id='test arxiv_id'
        )

        self.publication.keywords.set(self.keywords)

        self.add_compas_dataset_model_mutation = """
            mutation AddCompasDatasetModelMutation($input: AddCompasDatasetModelMutationInput!) {
                addCompasDatasetModel(input: $input) {
                    id
                }
            }
        """

        self.delete_compas_dataset_model_mutation = """
            mutation DeleteCompasDatasetModelMutation($input: DeleteCompasDatasetModelMutationInput!) {
                deleteCompasDatasetModel(input: $input) {
                    result
                }
            }
        """

        self.test_job_archive = SimpleUploadedFile(
            name='test.tar.gz',
            content=open('./publications/tests/test_data/test_job.tar.gz', 'rb').read(),
            content_type='application/gzip'
        )

        self.test_job_single = SimpleUploadedFile(
            name='COMPAS_Output.h5',
            content=open('./publications/tests/test_data/test_job/COMPAS_Output/COMPAS_Output.h5', 'rb').read(),
            content_type='application/x-bag'
        )

        self.archive_input = {
            'input': {
                'compasPublication': to_global_id('CompasPublication', self.publication.id),
                'compasModel': to_global_id('CompasModel', self.model.id),
                'file': self.test_job_archive
            }
        }

        self.single_input = {
            'input': {
                'compasPublication': to_global_id('CompasPublication', self.publication.id),
                'compasModel': to_global_id('CompasModel', self.model.id),
                'file': self.test_job_single
            }
        }

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
                            files
                        }
                    }
                }
            }
        """

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_add_compas_dataset_model_authenticated_archive(self):
        self.client.authenticate(self.user)

        response = self.client.execute(
            self.add_compas_dataset_model_mutation,
            self.archive_input
        )

        expected = {
            'addCompasDatasetModel': {
                'id': to_global_id('CompasDatasetModel', CompasDatasetModel.objects.last().id),
            }
        }

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(
            CompasDatasetModel.objects.filter(compas_publication=self.publication, compas_model=self.model).count(),
            1
        )

        files = [
            'BSE_Detailed_Output_0.h5',
            'gw151226evol.png',
            'COMPAS_Output.h5',
            'Run_Details',
            'BSE_grid.txt'
        ]

        self.assertEqual(5, Upload.objects.all().count())
        for f in files:
            self.assertTrue(
                Upload.objects.filter(file__contains=f, dataset_model=CompasDatasetModel.objects.last()).exists()
            )

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_add_compas_dataset_model_authenticated_single(self):
        self.client.authenticate(self.user)

        response = self.client.execute(
            self.add_compas_dataset_model_mutation,
            self.single_input
        )

        expected = {
            'addCompasDatasetModel': {
                'id': to_global_id('CompasDatasetModel', CompasDatasetModel.objects.last().id),
            }
        }

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(
            CompasDatasetModel.objects.filter(compas_publication=self.publication, compas_model=self.model).count(),
            1
        )

        self.assertEqual(Upload.objects.all().count(), 1)
        self.assertEqual(Upload.objects.last().file.name, 'publications/1/1/COMPAS_Output.h5')

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_add_compas_dataset_model_authenticated_not_publication_manager(self):
        self.client.authenticate(self.user)

        response = self.client.execute(
            self.add_compas_dataset_model_mutation,
            self.archive_input
        )

        expected = {
            'addCompasDatasetModel': None
        }

        self.assertEqual("You do not have permission to perform this action", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(
            CompasDatasetModel.objects.filter(compas_publication=self.publication, compas_model=self.model).count(),
            0
        )

    def test_add_publication_unauthenticated(self):
        response = self.client.execute(
            self.add_compas_dataset_model_mutation,
            self.archive_input
        )

        expected = {
            'addCompasDatasetModel': None
        }

        self.assertEqual("You do not have permission to perform this action", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(
            CompasDatasetModel.objects.filter(compas_publication=self.publication, compas_model=self.model).count(),
            0
        )

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_delete_compas_dataset_model_authenticated(self):
        self.client.authenticate(self.user)

        model = CompasDatasetModel.create_dataset_model(
            self.publication,
            self.model,
            self.test_job_archive
        )

        dataset_model_input = {
            'input': {
                'id': to_global_id('CompasDatasetModel', model.id),
            }
        }

        response = self.client.execute(
            self.delete_compas_dataset_model_mutation,
            dataset_model_input
        )

        expected = {
            'deleteCompasDatasetModel': {
                'result': True
            }
        }

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(CompasDatasetModel.objects.all().count(), 0)
        self.assertEqual(Upload.objects.all().count(), 0)

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[2])
    def test_delete_compas_dataset_model_authenticated_not_publication_manager(self):
        self.client.authenticate(self.user)

        model = CompasDatasetModel.create_dataset_model(
            self.publication,
            self.model,
            self.test_job_archive
        )

        dataset_model_input = {
            'input': {
                'id': to_global_id('CompasDatasetModel', model.id),
            }
        }

        response = self.client.execute(
            self.delete_compas_dataset_model_mutation,
            dataset_model_input
        )

        expected = {
            'deleteCompasDatasetModel': None
        }

        self.assertEqual("You do not have permission to perform this action", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(CompasDatasetModel.objects.all().count(), 1)
        self.assertEqual(Upload.objects.all().count(), 5)

    def test_delete_compas_dataset_model_unauthenticated(self):
        model = CompasDatasetModel.create_dataset_model(
            self.publication,
            self.model,
            self.test_job_archive
        )

        dataset_model_input = {
            'input': {
                'id': to_global_id('CompasDatasetModel', model.id),
            }
        }

        response = self.client.execute(
            self.delete_compas_dataset_model_mutation,
            dataset_model_input
        )

        expected = {
            'deleteCompasDatasetModel': None
        }

        self.assertEqual("You do not have permission to perform this action", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(CompasDatasetModel.objects.all().count(), 1)
        self.assertEqual(Upload.objects.all().count(), 5)

    @override_settings(PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS=[1])
    def test_delete_compas_dataset_model_not_exists(self):
        self.client.authenticate(self.user)

        model = CompasDatasetModel.create_dataset_model(
            self.publication,
            self.model,
            self.test_job_archive
        )

        dataset_model_input = {
            'input': {
                'id': to_global_id('CompasDatasetModel', model.id+1),
            }
        }

        response = self.client.execute(
            self.delete_compas_dataset_model_mutation,
            dataset_model_input
        )

        expected = {
            'deleteCompasDatasetModel': None
        }

        self.assertEqual("CompasDatasetModel matching query does not exist.", response.errors[0].message)
        self.assertDictEqual(expected, response.data)

        self.assertEqual(CompasPublication.objects.all().count(), 1)

    def test_compas_dataset_model_query_unauthenticated(self):
        CompasDatasetModel.create_dataset_model(
            self.publication,
            self.model,
            self.test_job_archive
        )

        response = self.client.execute(
            self.dataset_model_query
        )

        expected = {
            'compasDatasetModels': {
                'edges': [
                    {
                        'node': {
                            'id': 'Q29tcGFzRGF0YXNldE1vZGVsTm9kZTox',
                            'compasPublication': {
                                'id': 'Q29tcGFzUHVibGljYXRpb25Ob2RlOjE=',
                                'author': 'test author',
                                'title': 'test title',
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
                            },
                            'compasModel': {
                                'id': 'Q29tcGFzTW9kZWxOb2RlOjE=',
                                'name': 'test',
                                'summary': 'summary',
                                'description': 'description'
                            },
                            'files': [
                                '/compas/files/publications/1/1/COMPAS_Output/Detailed_Output/BSE_Detailed_Output_0.h5',
                                '/compas/files/publications/1/1/COMPAS_Output/Detailed_Output/gw151226evol.png',
                                '/compas/files/publications/1/1/COMPAS_Output/COMPAS_Output.h5',
                                '/compas/files/publications/1/1/COMPAS_Output/Run_Details',
                                '/compas/files/publications/1/1/BSE_grid.txt'
                            ]
                        }
                    }
                ]
            }
        }

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)

    def test_compas_dataset_model_query_authenticated(self):
        self.client.authenticate(self.user)

        CompasDatasetModel.create_dataset_model(
            self.publication,
            self.model,
            self.test_job_archive
        )

        response = self.client.execute(
            self.dataset_model_query
        )

        expected = {
            'compasDatasetModels': {
                'edges': [
                    {
                        'node': {
                            'id': 'Q29tcGFzRGF0YXNldE1vZGVsTm9kZTox',
                            'compasPublication': {
                                'id': 'Q29tcGFzUHVibGljYXRpb25Ob2RlOjE=',
                                'author': 'test author',
                                'title': 'test title',
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
                            },
                            'compasModel': {
                                'id': 'Q29tcGFzTW9kZWxOb2RlOjE=',
                                'name': 'test',
                                'summary': 'summary',
                                'description': 'description'
                            },
                            'files': [
                                '/compas/files/publications/1/1/COMPAS_Output/Detailed_Output/BSE_Detailed_Output_0.h5',
                                '/compas/files/publications/1/1/COMPAS_Output/Detailed_Output/gw151226evol.png',
                                '/compas/files/publications/1/1/COMPAS_Output/COMPAS_Output.h5',
                                '/compas/files/publications/1/1/COMPAS_Output/Run_Details',
                                '/compas/files/publications/1/1/BSE_grid.txt'
                            ]
                        }
                    }
                ]
            }
        }

        self.assertEqual(None, response.errors)
        self.assertDictEqual(expected, response.data)
