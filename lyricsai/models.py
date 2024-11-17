from django.db import models
import json

class Artist(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='songs')
    lyrics = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    countries = models.TextField(blank=True, null=True)
    error = models.TextField(blank=True, null=True)

    @property
    def countries_list(self):
        """Returns countries as a list or an empty list if countries is not valid JSON."""
        if self.countries:
            try:
                return json.loads(self.countries)
            except json.JSONDecodeError:
                return []  # Return an empty list if parsing fails
        return []

    def __str__(self):
        return self.title

