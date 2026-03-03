from django.db import models

class Author(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    biography = models.TextField(blank=True)
    date_of_birth = models.DateField()
    date_of_death = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"