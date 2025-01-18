from django.db import models

class ContactPage(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title

class ContactImage(models.Model):
    contact_page = models.ForeignKey(ContactPage, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='contact_images/')

    def __str__(self):
        return f"Image for {self.contact_page.title}"
    