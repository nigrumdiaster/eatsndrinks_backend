from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify 

class Blog(models.Model):
    title = models.CharField(max_length=500)  # Title of the news
    main_image = models.ImageField(upload_to='uploads/', blank=False, null=False, default='uploads/noimage.jpg')  # Main image for the news
    category = models.CharField(max_length=255)  # Category or tag for the news
    content = RichTextField()  # Rich text content of the news
    slug = models.SlugField(blank=True, null=True, max_length=550)  # Slug for the news URL
    created_at = models.DateTimeField(auto_now_add=True)  # Date and time when the news was created
    updated_at = models.DateTimeField(auto_now=True)  # Date and time when the news was last updated

    
    class Meta:
        verbose_name = "Bài Viết"
        verbose_name_plural = "Bài Viết"
    
    def save(self, *args, **kwargs):
        self.DuongDan = slugify(self.TieuDe)
        super(Blog, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.TieuDe
    
    