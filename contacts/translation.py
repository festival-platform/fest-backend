from modeltranslation.translator import translator, TranslationOptions
from .models import ContactPage

class ContactPageTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)  

translator.register(ContactPage, ContactPageTranslationOptions)
