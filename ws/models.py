from django.db import models
from django.conf import settings

from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.contrib.postgres.indexes import GinIndex

class NameModel(models.Model):
    name = models.CharField(max_length=255, default="")
    class Meta:
        abstract = True 


class OwnerModel(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        abstract = True

class NameOwnerModel(models.Model):
    name = models.CharField(max_length=255, default="", unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        abstract = True 


class SearchableModel(NameOwnerModel):
    search_name = SearchVectorField(null=True)

    class Meta:
        abstract = True
        indexes = [
            GinIndex(
                fields=[
                    'search_name',
                    ]
                )
            ]


    def index_components(self):
        return {
            'A': self.name,
        }