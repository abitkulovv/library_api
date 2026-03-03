from django.db import models
from django.conf import settings
from apps.books.models import Book

class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites"
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "book")
        indexes = [models.Index(fields=["user", "book"]),]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} -> {self.book.title}"