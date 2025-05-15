from django.db import models

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploaded_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    hash = models.CharField(max_length=64, default='', null=False)
    def __str__(self):
        return self.image.name
