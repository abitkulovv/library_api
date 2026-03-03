from django.db import models
from apps.authors.models import Author

class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    publication_date = models.DateField()
    authors = models.ManyToManyField(Author, related_name="books")

    class Meta:
        ordering = ["-publication_date"]

    def __str__(self):
        return self.title