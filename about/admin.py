from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from django.utils.html import format_html
from .models import AboutPage, AboutImage

class AboutImageInline(admin.TabularInline):
    model = AboutImage
    extra = 1
    fields = ('thumbnail', 'image',)
    readonly_fields = ('thumbnail',)

    def thumbnail(self, obj):
        if obj.image and obj.image.url:
            return format_html('<img src="{}" style="max-height:100px; max-width:100px;" />', obj.image.url)
        return "No Image"
    thumbnail.short_description = "Preview"

@admin.register(AboutPage)
class AboutPageAdmin(TranslationAdmin):
    inlines = [AboutImageInline]
    list_display = ('title',)
    search_fields = ('title',)
    