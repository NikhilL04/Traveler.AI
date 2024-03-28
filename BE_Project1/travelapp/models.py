from django.db import models
# Create your models here.
class Destinations(models.Model):
    near_city=models.CharField(max_length=100)
    place=models.CharField(max_length=100)
    image=models.ImageField(upload_to='images/')
    info=models.TextField()

class Verify(models.Model):
    username=models.CharField(max_length=100)
    email=models.EmailField()

class SignUp(models.Model):
    username=models.CharField(max_length=100)
    email=models.EmailField()
    password=models.CharField(max_length=100)
 
