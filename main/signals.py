from django.db.models.signals import post_save
from django.dispatch import receiver
from bot.settings.languages import languages
from .models import CategoryMod
from deep_translator import GoogleTranslator


@receiver(post_save, sender=CategoryMod)
def put_category_text(sender, created, instance, **kwargs):
    if created:
        name = instance.name_uz
        try:
            if not instance.name_ru: 
                instance.name_ru = GoogleTranslator(source='auto', target='ru').translate(name)
            if not instance.name_en: 
                instance.name_en = GoogleTranslator(source='auto', target='en').translate(name)
            instance.save()
        except Exception as error:
            print("Category error: ", error)
