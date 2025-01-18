from modeltranslation.translator import translator, TranslationOptions
from .models import AboutPage

class AboutPageTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)

translator.register(AboutPage, AboutPageTranslationOptions)