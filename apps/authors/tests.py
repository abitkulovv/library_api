from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User
from apps.authors.models import Author
import datetime


class AuthorModelTest(TestCase):

    def test_create_author(self):
        author = Author.objects.create(
            first_name="Leo",
            last_name="Tolstoy",
            biography="Russian novelist",
            date_of_birth=datetime.date(1828, 9, 9),
            date_of_death=datetime.date(1910, 11, 20),
        )
        self.assertEqual(author.first_name, "Leo")
        self.assertEqual(author.last_name, "Tolstoy")
        self.assertIsNotNone(author.id)

    def test_author_str(self):
        author = Author.objects.create(
            first_name="Leo",
            last_name="Tolstoy",
            date_of_birth=datetime.date(1828, 9, 9),
        )
        self.assertEqual(str(author), "Leo Tolstoy")

    def test_date_of_death_optional(self):
        author = Author.objects.create(
            first_name="Living",
            last_name="Author",
            date_of_birth=datetime.date(1980, 1, 1),
        )
        self.assertIsNone(author.date_of_death)

    def test_author_ordering(self):
        Author.objects.create(first_name="B", last_name="Zzz", date_of_birth=datetime.date(1980, 1, 1))
        Author.objects.create(first_name="A", last_name="Aaa", date_of_birth=datetime.date(1980, 1, 1))
        authors = list(Author.objects.all())
        self.assertEqual(authors[0].last_name, "Aaa")



def get_token(client, username="user", password="StrongPass123!"):
    User.objects.create_user(username=username, password=password)
    r = client.post("/api/auth/login/", {"username": username, "password": password})
    return r.data["access"]


def make_author(**kwargs):
    defaults = dict(
        first_name="Test",
        last_name="Author",
        biography="Bio",
        date_of_birth=datetime.date(1970, 1, 1),
    )
    defaults.update(kwargs)
    return Author.objects.create(**defaults)




class AuthorViewSetTest(APITestCase):

    def setUp(self):
        token = get_token(self.client)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_list_authors(self):
        make_author(last_name="Smith")
        make_author(last_name="Jones")
        response = self.client.get("/api/authors/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_author(self):
        data = {
            "first_name": "Mark",
            "last_name": "Twain",
            "biography": "American author",
            "date_of_birth": "1835-11-30",
            "date_of_death": "1910-04-21",
        }
        response = self.client.post("/api/authors/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["last_name"], "Twain")

    def test_create_author_missing_required_fields(self):
        response = self.client.post("/api/authors/", {"first_name": "Only"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_author(self):
        author = make_author(first_name="Jane", last_name="Austen")
        response = self.client.get(f"/api/authors/{author.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["last_name"], "Austen")

    def test_retrieve_nonexistent_author(self):
        response = self.client.get("/api/authors/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_author(self):
        author = make_author()
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "date_of_birth": "1970-01-01",
        }
        response = self.client.patch(f"/api/authors/{author.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Updated")

    def test_delete_author(self):
        author = make_author()
        response = self.client.delete(f"/api/authors/{author.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Author.objects.filter(id=author.id).exists())

    def test_full_name_field_in_response(self):
        author = make_author(first_name="John", last_name="Doe")
        response = self.client.get(f"/api/authors/{author.id}/")
        self.assertEqual(response.data["full_name"], "John Doe")

    def test_unauthenticated_request_denied(self):
        self.client.credentials()
        response = self.client.get("/api/authors/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)