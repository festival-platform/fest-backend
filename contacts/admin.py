from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin
from .models import ContactPage, ContactImage

class ContactImageInline(admin.TabularInline):
    model = ContactImage
    extra = 1
    fields = ('thumbnail', 'image',)
    readonly_fields = ('thumbnail',)

    def thumbnail(self, obj):
        if obj.image and obj.image.url:
            return format_html('<img src="{}" style="max-height:100px; max-width:100px;" />', obj.image.url)
        return "No Image"
    thumbnail.short_description = "Preview"

@admin.register(ContactPage)
class ContactPageAdmin(TranslationAdmin):
    inlines = [ContactImageInline]
    list_display = ('title', 'phone', 'email')
    search_fields = ('title', 'address')
