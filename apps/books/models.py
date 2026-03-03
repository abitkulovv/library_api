from django.db import models
from apps.authors.models import Author

class Book(models.Model):

    class Genre(models.TextChoices):
        FICTION = "FICTION", "Fiction"
        NONFICTION = "NONFICTION", "Non-Fiction"
        SCIENCE = "SCIENCE", "Science"
        FANTASY = "FANTASY", "Fantasy"
        OTHER = "OTHER", "Other"

    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    isbn = models.CharField(max_length=13, unique=True)
    publication_date = models.DateField()
    genre = models.CharField(
        max_length=20,
        choices=Genre.choices,
        default=Genre.OTHER,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    authors = models.ManyToManyField(Author, related_name="books")

    class Meta:
        ordering = ["-publication_date"]
        indexes = [
            models.Index(fields=["publication_date"]),
            models.Index(fields=["isbn"]),
        ]

    def __str__(self):
        return self.title