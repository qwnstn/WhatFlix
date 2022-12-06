from django.db import models
from django.conf import settings
# Create your models here.

class Genre(models.Model):
    name = models.CharField(max_length=50)


class Movie(models.Model):
    title = models.CharField(max_length=100)
    movie_id = models.CharField(max_length=10)
    poster_path = models.CharField(max_length=200, null=True)
    release_date = models.DateField()
    overview = models.TextField()
    video_path = models.CharField(max_length=100, null=True)
    genres = models.ManyToManyField(Genre)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="like_movies")
    vote_average = models.FloatField()
    recommend_movie_id = models.CharField(max_length=100)
    
    
class Provider(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    provider_link = models.CharField(max_length=200)
    provider_logo_path = models.CharField(max_length=200)

class Cast(models.Model):
    name = models.CharField(max_length=50)
    known_for_department = models.CharField(max_length=20)
    movie_id = models.CharField(max_length=10)
    credit_id = models.CharField(max_length=50)

class Poster(models.Model):
    movie_id = models.CharField(max_length=100)
    file_path = models.CharField(max_length=200)

class History(models.Model):
    user_id = models.IntegerField()
    movie_id = models.CharField(max_length=10)
    genres = models.IntegerField()
    score = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

class Cinema(models.Model):
    name = models.CharField(max_length=50)
    metropolitan_city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    latitude = models.FloatField()
    altitude = models.FloatField()