from django.db import models
from apps.users.models import User
from apps.books.models import Book

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="favorited_by")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "book")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user.username} -> {self.book.title}"