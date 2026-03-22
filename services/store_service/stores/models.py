from django.db import models


class Store(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"({self.name}: {self.description} "
            + f"Created at {self.created_at} in {self.city})"
        )
