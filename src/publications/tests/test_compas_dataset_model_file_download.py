from pathlib import Path
import uuid
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, Client
from django.urls import reverse
from graphql_relay import to_global_id

from compasui.tests.testcases import CompasTestCase
from publications.models import CompasModel, CompasPublication, Keyword
from publications.tests.test_utils import silence_errors

User = get_user_model()


def create_model_publication(i=1):
    model = CompasModel.create_model(f'test {i}', 'summary', 'description')

    keywords = [
        Keyword.create_keyword(f'keyword1{i}'),
        Keyword.create_keyword(f'keyword2{i}'),
        Keyword.create_keyword(f'keyword3{i}')
    ]

    publication = CompasPublication.create_publication(
        author=f'test author {i}',
        title=f'test title {i}',
        arxiv_id=f'test arxiv_id {i}'
    )

    publication.keywords.set(keywords)

    return model, publication


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
class TestUploadedJobFileDownload(CompasTestCase):
    def setUp(self):
        self.user = User.objects.create(username="buffy", first_name="buffy", last_name="summers")
        self.client.authenticate(self.user)

        self.model, self.publication = create_model_publication()

        response = self.client.execute(
            """
                query {
                    generateCompasDatasetModelUploadToken {
                        token
                    }
                }
            """
        )

        self.test_input = {
            'input': {
                'uploadToken': response.data['generateCompasDatasetModelUploadToken']['token'],
                'compasPublication': to_global_id('CompasPublication', self.publication.id),
                'compasModel': to_global_id('CompasModel', self.model.id),
                'jobFile': SimpleUploadedFile(
                    name='test.tar.gz',
                    content=open('./publications/tests/test_data/test_job.tar.gz', 'rb').read(),
                    content_type='application/gzip'
                )
            }
        }

        response = self.client.execute(
            """
                mutation UploadCompasDatasetModelMutation($input: UploadCompasDatasetModelMutationInput!) {
                    uploadCompasDatasetModel(input: $input) {
                        id
                    }
                }
            """,
            self.test_input,
        )

        self.dataset_id = response.data['uploadCompasDatasetModel']['id']

        self.query = """
            query ($id: ID!){
                compasDatasetModel (id: $id) {
                    files {
                        path
                        fileSize
                        downloadToken
                    }
                }
            }
        """

        self.http_client = Client()

    def generate_file_download_tokens(self):
        response = self.client.execute(self.query, {'id': self.dataset_id})
        download_tokens = [f['downloadToken'] for f in response.data['compasDatasetModel']['files']]
        return download_tokens, response

    @silence_errors
    def test_no_token(self):
        response = self.http_client.get(f'{reverse(viewname="file_download")}')
        self.assertEqual(response.status_code, 404)

    @silence_errors
    def test_invalid_token(self):
        download_tokens, _ = self.generate_file_download_tokens()

        token = download_tokens[0] + "_not_real"

        response = self.http_client.get(f'{reverse(viewname="file_download")}?fileId={token}')
        self.assertEqual(response.status_code, 404)

        response = self.http_client.get(f'{reverse(viewname="file_download")}?fileId={uuid.uuid4()}')
        self.assertEqual(response.status_code, 404)

    @silence_errors
    def test_success(self):
        download_tokens, response = self.generate_file_download_tokens()

        for f in response.data['compasDatasetModel']['files']:
            token = f['downloadToken']
            path = Path(f['path'])

            response = self.http_client.get(f'{reverse(viewname="file_download")}?fileId={token}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["Content-Type"], "application/octet-stream")
            self.assertEqual(
                response.headers["Content-Disposition"],
                f'inline; filename="{path.name}"',
            )

            content = b"".join(list(response))

            with open(path, "rb") as f:
                self.assertEqual(content, f.read())
