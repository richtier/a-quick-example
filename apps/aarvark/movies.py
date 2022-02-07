# C2006 (huge-max-length)
# C2008 (deprecated-nullboolean-field)
from django.db import models


class Movie(models.Model):
    movie_id = models.IntegerField()
    imbd_id = models.CharField(max_length=200)
    movie_title = models.CharField(max_length=500)
    genero = models.CharField(max_length=200)
    original_language = models.CharField(max_length=200)
    overview = models.TextField()
    poster_path = models.CharField(max_length=5000)
