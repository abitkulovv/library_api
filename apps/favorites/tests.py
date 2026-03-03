from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User
from apps.authors.models import Author
from apps.books.models import Book
from apps.favorites.models import Favorite
import datetime


def create_user(username, password="StrongPass123!"):
    return User.objects.create_user(username=username, password=password)


def get_token(client, user, password="StrongPass123!"):
    r = client.post("/api/auth/login/", {"username": user.username, "password": password})
    return r.data["access"]


def make_author():
    return Author.objects.create(
        first_name="Auth",
        last_name="Or",
        date_of_birth=datetime.date(1970, 1, 1)
    )


def make_book(isbn="1234567890000", **kwargs):
    defaults = dict(
        title="Fav Book",
        isbn=isbn,
        publication_date=datetime.date(2020, 1, 1),
        genre=Book.Genre.FICTION,
    )
    defaults.update(kwargs)
    return Book.objects.create(**defaults)


class FavoriteModelTest(TestCase):

    def setUp(self):
        self.user = create_user("favmodeluser")
        self.book = make_book()

    def test_create_favorite(self):
        fav = Favorite.objects.create(user=self.user, book=self.book)
        self.assertEqual(fav.user, self.user)
        self.assertEqual(fav.book, self.book)

    def test_favorite_str(self):
        fav = Favorite.objects.create(user=self.user, book=self.book)
        self.assertIn(self.user.username, str(fav))
        self.assertIn(self.book.title, str(fav))

    def test_unique_together_constraint(self):
        Favorite.objects.create(user=self.user, book=self.book)
        from django.db import IntegrityError
        with self.assertRaises(Exception):
            Favorite.objects.create(user=self.user, book=self.book)

    def test_cascade_delete_user(self):
        fav = Favorite.objects.create(user=self.user, book=self.book)
        self.user.delete()
        self.assertFalse(Favorite.objects.filter(id=fav.id).exists())

    def test_cascade_delete_book(self):
        fav = Favorite.objects.create(user=self.user, book=self.book)
        self.book.delete()
        self.assertFalse(Favorite.objects.filter(id=fav.id).exists())


class FavoriteViewSetTest(APITestCase):

    def setUp(self):
        self.user = create_user("favviewuser")
        self.other_user = create_user("otheruser")
        self.token = get_token(self.client, self.user)
        self.book1 = make_book(isbn="1000000000001")
        self.book2 = make_book(isbn="1000000000002")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_add_favorite(self):
        response = self.client.post("/api/favorites/", {"book_id": self.book1.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Favorite.objects.filter(user=self.user, book=self.book1).exists())

    def test_add_duplicate_favorite_rejected(self):
        self.client.post("/api/favorites/", {"book_id": self.book1.id})
        response = self.client.post("/api/favorites/", {"book_id": self.book1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_favorites_only_own(self):
        Favorite.objects.create(user=self.user, book=self.book1)
        Favorite.objects.create(user=self.other_user, book=self.book2)
        response = self.client.get("/api/favorites/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_delete_own_favorite(self):
        fav = Favorite.objects.create(user=self.user, book=self.book1)
        response = self.client.delete(f"/api/favorites/{fav.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Favorite.objects.filter(id=fav.id).exists())

    def test_delete_others_favorite_denied(self):
        other_fav = Favorite.objects.create(user=self.other_user, book=self.book2)
        response = self.client.delete(f"/api/favorites/{other_fav.id}/")
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_unauthenticated_denied(self):
        self.client.credentials()
        response = self.client.get("/api/favorites/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_favorite_contains_book_detail(self):
        Favorite.objects.create(user=self.user, book=self.book1)
        response = self.client.get("/api/favorites/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("title", response.data[0]["book"])

    def test_clear_favorites(self):
        Favorite.objects.create(user=self.user, book=self.book1)
        Favorite.objects.create(user=self.user, book=self.book2)
        response = self.client.delete("/api/favorites/clear/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Favorite.objects.filter(user=self.user).count(), 0)

    def test_clear_only_own_favorites(self):
        Favorite.objects.create(user=self.user, book=self.book1)
        Favorite.objects.create(user=self.other_user, book=self.book2)
        self.client.delete("/api/favorites/clear/")
        self.assertTrue(Favorite.objects.filter(user=self.other_user).exists())

    def test_clear_empty_favorites(self):
        response = self.client.delete("/api/favorites/clear/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)