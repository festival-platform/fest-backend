from django.db import models

class AboutPage(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

class AboutImage(models.Model):
    about_page = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='about_images/')

    def __str__(self):
        return f"Image for {self.about_page.title}"
