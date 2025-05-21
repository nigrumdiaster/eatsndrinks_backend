from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    mainimage = models.ImageField(upload_to="restaurant_images/", blank=True, null=True)
    description = models.TextField()
    address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
