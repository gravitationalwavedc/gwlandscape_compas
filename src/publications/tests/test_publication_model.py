from django.test import testcases

from publications.models import CompasPublication, Keyword


class TestCompasPublicationModel(testcases.TestCase):
    def setUp(self):
        self.keywords_ids = [
            Keyword.create_keyword("keyword1").id,
            Keyword.create_keyword("keyword2").id,
            Keyword.create_keyword("keyword3").id,
        ]

        self.publication_input_required = {
            "author": "test author",
            "title": "test title",
            "arxiv_id": "test arxiv_id",
        }

        self.publication_input_full = {
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
            "keywords": self.keywords_ids,
        }

        self.publication_updated_full = {
            "author": "new author",
            "title": "new title",
            "arxiv_id": "new arxiv_id",
            "published": False,
            "year": 1984,
            "journal": "new journal",
            "journal_doi": "new journal doi",
            "dataset_doi": "new dataset doi",
            "description": "new description",
            "public": False,
            "download_link": "new download link",
        }

    def test_create(self):
        CompasPublication.create_publication(**self.publication_input_required)
        self.assertEqual(
            1,
            CompasPublication.objects.filter(**self.publication_input_required).count(),
        )

        CompasPublication.create_publication(**self.publication_input_full)

        del self.publication_input_full["keywords"]

        for kw in Keyword.objects.all():
            self.assertEqual(
                CompasPublication.objects.filter(
                    **self.publication_input_full, keywords=kw
                ).count(),
                1,
            )

    def test_delete(self):
        publication = CompasPublication.create_publication(
            **self.publication_input_required
        )
        CompasPublication.delete_publication(publication.id)

        with self.assertRaises(
            CompasPublication.DoesNotExist,
            msg="CompasPublication was deleted successfully when it should have failed",
        ):
            CompasPublication.delete_publication(publication.id)

    def test_update_single(self):
        publication = CompasPublication.create_publication(
            **self.publication_input_full
        )
        keywords = self.publication_input_full.pop("keywords")

        for key, val in self.publication_input_full.items():
            self.assertEqual(getattr(publication, key), val)

            CompasPublication.update_publication(
                publication.id, **{key: self.publication_updated_full[key]}
            )
            publication.refresh_from_db()

            self.assertEqual(
                getattr(publication, key), self.publication_updated_full[key]
            )

        self.assertEqual(
            list(publication.keywords.values_list("id", flat=True)), keywords
        )

        CompasPublication.update_publication(publication.id, keywords=[])
        publication.refresh_from_db()

        self.assertEqual(list(publication.keywords.values_list("id", flat=True)), [])

    def test_update_multiple(self):
        publication = CompasPublication.create_publication(
            **self.publication_input_full
        )
        keywords = self.publication_input_full.pop("keywords")

        for key, val in self.publication_input_full.items():
            self.assertEqual(getattr(publication, key), val)

        self.assertEqual(
            list(publication.keywords.values_list("id", flat=True)), keywords
        )

        CompasPublication.update_publication(
            publication.id, **self.publication_updated_full, keywords=[]
        )
        publication.refresh_from_db()

        for key, val in self.publication_updated_full.items():
            self.assertEqual(getattr(publication, key), val)

        self.assertEqual(list(publication.keywords.values_list("id", flat=True)), [])
