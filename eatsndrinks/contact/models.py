from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    phone_number = models.CharField(max_length=11, null=False, blank=False)
    subject = models.CharField(max_length=500, blank=True)  # Made blank=True to match typical optional fields
    content = models.TextField() 

    class Meta:
        verbose_name = "Liên Hệ"
        verbose_name_plural = "Liên Hệ"
        
    def __str__(self):
        return f"{self.name} - {self.subject}"
