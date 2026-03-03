from celery import shared_task
from datetime import date, timedelta
from django.core.mail import send_mail
from django.conf import settings
from apps.books.models import Book
from django.contrib.auth import get_user_model


User = get_user_model()


@shared_task
def send_new_books_notifications():
    yesterday = date.today() - timedelta(days=1)
    new_books = Book.objects.filter(created_at__date__gte=yesterday)
    if not new_books.exists():
        return "No new books"

    users = User.objects.filter(is_active=True)
    for user in users:
        titles = "\n".join([book.title for book in new_books])
        subject = "New Books Added in the Last 24 Hours"
        message = f"Hi {user.username},\n\nThe following new books have been added:\n{titles}\n\nEnjoy reading!"
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    return f"Notified {users.count()} users"


@shared_task
def send_anniversary_books_notifications():
    today = date.today()
    users = User.objects.filter(is_active=True)
    anniversary_books = Book.objects.filter(
        publication_date__month=today.month,
        publication_date__day=today.day,
    )

    for book in anniversary_books:
        years = today.year - book.publication_date.year
        if years in [5, 10, 20]:
            for user in users:
                subject = f"Anniversary: {book.title}"
                message = f"Hi {user.username},\n\nThe book '{book.title}' was published {years} years ago today.\nCelebrate this anniversary with us!"
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
    return f"Notified {users.count()} users for {len(anniversary_books)} books"