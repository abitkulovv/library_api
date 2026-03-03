from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User
from apps.authors.models import Author
from apps.books.models import Book
import datetime


def get_token(client, username="bookuser", password="StrongPass123!"):
    User.objects.get_or_create(username=username, defaults={"password": "x"})
    User.objects.filter(username=username).delete()
    User.objects.create_user(username=username, password=password)
    r = client.post("/api/auth/login/", {"username": username, "password": password})
    return r.data["access"]


def make_author(**kwargs):
    defaults = dict(first_name="A", last_name="Author", date_of_birth=datetime.date(1970, 1, 1))
    defaults.update(kwargs)
    return Author.objects.create(**defaults)


def make_book(authors=None, **kwargs):
    defaults = dict(
        title="Test Book",
        summary="Summary",
        isbn="1234567890123",
        publication_date=datetime.date(2020, 1, 1),
        genre=Book.Genre.FICTION,
    )
    defaults.update(kwargs)
    book = Book.objects.create(**defaults)
    if authors:
        book.authors.set(authors)
    return book


class BookModelTest(TestCase):

    def setUp(self):
        self.author = make_author()

    def test_create_book(self):
        book = make_book(authors=[self.author], isbn="0000000000001")
        self.assertEqual(book.title, "Test Book")
        self.assertIsNotNone(book.id)

    def test_book_str(self):
        book = make_book(title="My Book", isbn="0000000000002")
        self.assertEqual(str(book), "My Book")

    def test_isbn_unique(self):
        make_book(isbn="0000000000003")
        from django.db import IntegrityError
        with self.assertRaises(Exception):
            make_book(isbn="0000000000003")

    def test_book_ordering(self):
        make_book(isbn="0000000000004", publication_date=datetime.date(2010, 1, 1))
        make_book(isbn="0000000000005", publication_date=datetime.date(2020, 1, 1))
        books = list(Book.objects.all())
        self.assertGreaterEqual(books[0].publication_date, books[1].publication_date)

    def test_default_genre(self):
        book = Book.objects.create(
            title="No Genre Book",
            isbn="0000000000006",
            publication_date=datetime.date(2020, 1, 1),
        )
        self.assertEqual(book.genre, Book.Genre.OTHER)

    def test_created_at_auto_set(self):
        book = make_book(isbn="0000000000007")
        self.assertIsNotNone(book.created_at)

    def test_many_to_many_authors(self):
        a1 = make_author(last_name="One")
        a2 = make_author(last_name="Two")
        book = make_book(authors=[a1, a2], isbn="0000000000008")
        self.assertEqual(book.authors.count(), 2)


class BookViewSetTest(APITestCase):

    def setUp(self):
        token = get_token(self.client)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.author = make_author()

    def _book_data(self, isbn="9780000000001"):
        return {
            "title": "New Book",
            "summary": "A great read",
            "isbn": isbn,
            "publication_date": "2021-06-01",
            "genre": "FICTION",
            "author_ids": [self.author.id],
        }

    def test_list_books(self):
        make_book(isbn="1111111111111")
        make_book(isbn="2222222222222")
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_book(self):
        response = self.client.post("/api/books/", self._book_data())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Book")

    def test_create_book_duplicate_isbn(self):
        make_book(isbn="9780000000001")
        response = self.client.post("/api/books/", self._book_data(isbn="9780000000001"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_book_missing_required_fields(self):
        response = self.client.post("/api/books/", {"title": "Only Title"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_book(self):
        book = make_book(isbn="3333333333333")
        response = self.client.get(f"/api/books/{book.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["isbn"], "3333333333333")

    def test_retrieve_nonexistent_book(self):
        response = self.client.get("/api/books/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_book(self):
        book = make_book(isbn="4444444444444")
        response = self.client.patch(f"/api/books/{book.id}/", {"title": "Updated"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated")

    def test_delete_book(self):
        book = make_book(isbn="5555555555555")
        response = self.client.delete(f"/api/books/{book.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())

    def test_unauthenticated_denied(self):
        self.client.credentials()
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authors_nested_in_response(self):
        book = make_book(authors=[self.author], isbn="6666666666666")
        response = self.client.get(f"/api/books/{book.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["authors"]), 1)
        self.assertIn("full_name", response.data["authors"][0])


class BookFilterTest(APITestCase):

    def setUp(self):
        token = get_token(self.client, username="filteruser")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.author1 = make_author(last_name="FilterA")
        self.author2 = make_author(last_name="FilterB")
        self.book1 = make_book(
            isbn="7777777777771",
            genre=Book.Genre.FICTION,
            publication_date=datetime.date(2015, 1, 1),
            authors=[self.author1],
        )
        self.book2 = make_book(
            isbn="7777777777772",
            genre=Book.Genre.SCIENCE,
            publication_date=datetime.date(2022, 6, 1),
            authors=[self.author2],
        )

    def test_filter_by_genre(self):
        response = self.client.get("/api/books/?genre=FICTION")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["genre"], "FICTION")

    def test_filter_by_author(self):
        response = self.client.get(f"/api/books/?authors={self.author1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_publication_date_range(self):
        response = self.client.get("/api/books/?publication_date_after=2020-01-01&publication_date_before=2023-01-01")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["isbn"], "7777777777772")