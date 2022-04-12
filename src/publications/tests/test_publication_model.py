from django.test import testcases
from graphql_relay import to_global_id

from publications.models import CompasPublication, Keyword


class TestCompasPublicationModel(testcases.TestCase):
    def setUp(self):
        self.keywords_ids = [
            to_global_id('KeywordNode', Keyword.create_keyword('keyword1').id),
            to_global_id('KeywordNode', Keyword.create_keyword('keyword2').id),
            to_global_id('KeywordNode', Keyword.create_keyword('keyword3').id),
        ]

        self.publication_input_required = {
            'author': 'test author',
            'title': 'test title',
            'arxiv_id': 'test arxiv_id'
        }

        self.publication_input_optional = {
            'author': 'test author',
            'title': 'test title',
            'arxiv_id': 'test arxiv_id',
            'published': True,
            'year': 1983,
            'journal': 'test journal',
            'journal_doi': 'test journal doi',
            'dataset_doi': 'test dataset doi',
            'description': 'test description',
            'public': True,
            'download_link': 'test download link',
            'keywords': self.keywords_ids
        }

    def test_create(self):
        CompasPublication.create_publication(**self.publication_input_required)
        self.assertEqual(1, CompasPublication.objects.filter(**self.publication_input_required).count())

        CompasPublication.create_publication(**self.publication_input_optional)

        del self.publication_input_optional['keywords']

        for kw in Keyword.objects.all():
            self.assertEqual(
                CompasPublication.objects.filter(
                    **self.publication_input_optional,
                    keywords=kw
                ).count(),
                1
            )

    def test_delete(self):
        publication = CompasPublication.create_publication(**self.publication_input_required)
        CompasPublication.delete_publication(publication.id)

        try:
            CompasPublication.delete_publication(publication.id)
            self.fail("CompasPublication was deleted successfully when it should have failed")
        except CompasPublication.DoesNotExist:
            pass
