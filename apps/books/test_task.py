from django.test import TestCase
from unittest.mock import patch, call
from datetime import date, timedelta
from apps.books.models import Book
from apps.authors.models import Author
from apps.users.models import User
from apps.books.tasks import send_new_books_notifications, send_anniversary_books_notifications


def make_author():
    return Author.objects.create(
        first_name="A", last_name="B", date_of_birth=date(1970, 1, 1)
    )


def make_book(isbn, publication_date=None, created_at_offset_days=0):
    """Create a book; created_at is auto, so we use update() to adjust."""
    book = Book.objects.create(
        title=f"Book {isbn}",
        isbn=isbn,
        publication_date=publication_date or date(2020, 1, 1),
        genre=Book.Genre.FICTION,
    )
    if created_at_offset_days != 0:
        from django.utils import timezone
        Book.objects.filter(pk=book.pk).update(
            created_at=timezone.now() - timedelta(days=created_at_offset_days)
        )
        book.refresh_from_db()
    return book


class SendNewBooksNotificationsTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="u1", email="u1@example.com", password="Pass123!"
        )
        self.user2 = User.objects.create_user(
            username="u2", email="u2@example.com", password="Pass123!"
        )

    @patch("apps.books.tasks.send_mail")
    def test_sends_mail_to_all_active_users(self, mock_send):
        make_book("1111111111111")  # created just now (within 24h)
        result = send_new_books_notifications()
        self.assertEqual(mock_send.call_count, 2)
        self.assertIn("Notified 2", result)

    @patch("apps.books.tasks.send_mail")
    def test_no_new_books_skips_mail(self, mock_send):
        # Make a book that's "old" by updating created_at to 2 days ago
        make_book("2222222222222", created_at_offset_days=2)
        result = send_new_books_notifications()
        mock_send.assert_not_called()
        self.assertEqual(result, "No new books")

    @patch("apps.books.tasks.send_mail")
    def test_inactive_user_excluded(self, mock_send):
        self.user2.is_active = False
        self.user2.save()
        make_book("3333333333333")
        send_new_books_notifications()
        self.assertEqual(mock_send.call_count, 1)
        called_email = mock_send.call_args[0][3][0]
        self.assertEqual(called_email, "u1@example.com")

    @patch("apps.books.tasks.send_mail")
    def test_email_contains_book_title(self, mock_send):
        make_book("4444444444444")
        Book.objects.filter(isbn="4444444444444").update(title="Special Title")
        send_new_books_notifications()
        message_body = mock_send.call_args_list[0][0][1]
        self.assertIn("Special Title", message_body)

    @patch("apps.books.tasks.send_mail")
    def test_no_users_no_mail(self, mock_send):
        User.objects.all().delete()
        make_book("5555555555555")
        send_new_books_notifications()
        mock_send.assert_not_called()


class SendAnniversaryBooksNotificationsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="anniv_user", email="anniv@example.com", password="Pass123!"
        )

    def _anniversary_date(self, years_ago):
        today = date.today()
        return date(today.year - years_ago, today.month, today.day)

    @patch("apps.books.tasks.send_mail")
    def test_5_year_anniversary_sends_mail(self, mock_send):
        make_book("6666666666661", publication_date=self._anniversary_date(5))
        result = send_anniversary_books_notifications()
        mock_send.assert_called_once()
        subject = mock_send.call_args[0][0]
        self.assertIn("Anniversary", subject)

    @patch("apps.books.tasks.send_mail")
    def test_10_year_anniversary_sends_mail(self, mock_send):
        make_book("6666666666662", publication_date=self._anniversary_date(10))
        send_anniversary_books_notifications()
        mock_send.assert_called_once()

    @patch("apps.books.tasks.send_mail")
    def test_20_year_anniversary_sends_mail(self, mock_send):
        make_book("6666666666663", publication_date=self._anniversary_date(20))
        send_anniversary_books_notifications()
        mock_send.assert_called_once()

    @patch("apps.books.tasks.send_mail")
    def test_non_anniversary_year_no_mail(self, mock_send):
        make_book("6666666666664", publication_date=self._anniversary_date(7))
        send_anniversary_books_notifications()
        mock_send.assert_not_called()

    @patch("apps.books.tasks.send_mail")
    def test_wrong_day_no_mail(self, mock_send):
        today = date.today()
        wrong_day = date(today.year - 5, today.month, 1)
        if wrong_day.day != today.day:
            make_book("6666666666665", publication_date=wrong_day)
            send_anniversary_books_notifications()
            mock_send.assert_not_called()

    @patch("apps.books.tasks.send_mail")
    def test_email_mentions_years(self, mock_send):
        make_book("6666666666666", publication_date=self._anniversary_date(10))
        send_anniversary_books_notifications()
        message = mock_send.call_args[0][1]
        self.assertIn("10", message)

    @patch("apps.books.tasks.send_mail")
    def test_multiple_anniversary_books(self, mock_send):
        make_book("7777777777771", publication_date=self._anniversary_date(5))
        make_book("7777777777772", publication_date=self._anniversary_date(10))
        send_anniversary_books_notifications()
        self.assertEqual(mock_send.call_count, 2)

    @patch("apps.books.tasks.send_mail")
    def test_inactive_user_excluded(self, mock_send):
        self.user.is_active = False
        self.user.save()
        make_book("8888888888881", publication_date=self._anniversary_date(5))
        send_anniversary_books_notifications()
        mock_send.assert_not_called()