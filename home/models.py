from django.db import models

# Create your models here.
class Login(models.Model):
    username = models.CharField(max_length=122)
    password = models.CharField(max_length=12)

    def __str__(self) :
        return self.username

class sen_locc(models.Model):
    lat = models.FloatField(max_length=10)
    lon = models.FloatField(max_length=100)

class final_sens(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()

class db_sens(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()

class hospital_db(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()

class hospital_name(models.Model):
    h_name = models.CharField(max_length=122)