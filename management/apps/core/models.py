from django.db import models


class TimestampedModel(models.Model):
    creation_date = models.DateTimeField(
        auto_now_add=True
    )
    modification_date = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        abstract = True
