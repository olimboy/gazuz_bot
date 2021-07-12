from django.db import models


# Create your models here.

class User(models.Model):
    # @TODO make fill columns
    id = models.BigIntegerField(primary_key=True)
    province_id = models.CharField(max_length=30)
    district_id = models.CharField(max_length=30)
    account = models.CharField(max_length=30)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.id}'


class Province(User):
    class Meta:
        managed = False


class District(User):
    class Meta:
        managed = False
