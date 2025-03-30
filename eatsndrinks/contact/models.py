from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    subject = models.CharField(max_length=500, blank=True)  # Made blank=True to match typical optional fields
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_replied = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Liên Hệ"
        verbose_name_plural = "Liên Hệ"
        
    def __str__(self):
        return f"{self.name} - {self.subject}"
