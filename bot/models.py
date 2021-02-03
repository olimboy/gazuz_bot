from django.db import models

# Create your models here.

class User(models.Model):
    # @TODO make fill columns
    # add user current path
    id = models.BigIntegerField(primary_key=True)
    province_id = models.CharField(max_length=30)
    district_id = models.CharField(max_length=30)
    account = models.CharField(max_length=30)