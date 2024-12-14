from modeltranslation.translator import translator, TranslationOptions
from .models import Event

class EventTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)

translator.register(Event, EventTranslationOptions)
