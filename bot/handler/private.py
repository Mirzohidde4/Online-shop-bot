import django, os
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from asgiref.sync import sync_to_async
from main.models import UserMod, CategoryMod, ProductMod
from ..settings.states import UserState
from ..settings.buttons import CreateInline, Createreply
from ..settings.languages import languages
from ..settings.functions import get_user_language


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
user_private_router = Router()


@user_private_router.message(CommandStart())
async def command_start(message: Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    lang = await get_user_language(user_id)
    user_filter = await sync_to_async(UserMod.objects.filter(user_id=user_id).first)()
    
    if not user_filter: await sync_to_async(UserMod.objects.create)(user_id=user_id, user_name=username, full_name=full_name, language='uz')
    await message.answer(text=lang['start'].replace('full_name', full_name), 
        reply_markup=CreateInline({lang['product_btn']:'get_products', lang['set_lang']:f"set_language", lang['info']:'get_information'}, just=(1, 2)))


@user_private_router.callback_query(F.data == 'get_products')
async def get_products(call: CallbackQuery):
    user_id = call.from_user.id
    user_filter = await sync_to_async(UserMod.objects.filter(user_id=user_id).first)()
    category_filter = await sync_to_async(list)(CategoryMod.objects.all())
    lang = languages[user_filter.language]

    if user_filter.language == 'uz':
        markup = Createreply(*(i.name_uz for i in category_filter), lang['back'])
    elif user_filter.language == 'ru':    
        markup = Createreply(*(i.name_ru for i in category_filter), lang['back'])
    elif user_filter.language == 'en':    
        markup = Createreply(*(i.name_en for i in category_filter), lang['back'])
    
    await call.message.delete()
    await call.message.answer(text=lang['category_txt'], reply_markup=markup)


@user_private_router.callback_query(F.data == 'set_language')
async def set_language(call: CallbackQuery):
    user_id = call.from_user.id
    user_filter = await sync_to_async(UserMod.objects.filter(user_id=user_id).first)()
    lang = languages[user_filter.language]
    
    await call.message.delete()
    if user_filter.language == 'uz': 
        await call.message.answer(text=lang['lang_text'], 
            reply_markup=CreateInline({lang['lang_ru']:'change_lang_ru', lang['lang_en']:'change_lang_en', lang['back']: 'change_lang_back'}))
    elif user_filter.language == 'ru':
        await call.message.answer(text=lang['lang_text'], 
            reply_markup=CreateInline({lang['lang_uz']:'change_lang_uz', lang['lang_en']:'change_lang_en', lang['back']: 'change_lang_back'}))
    elif user_filter.language == 'en':
        await call.message.answer(text=lang['lang_text'], 
            reply_markup=CreateInline({lang['lang_uz']:'change_lang_uz', lang['lang_ru']:'change_lang_ru', lang['back']: 'change_lang_back'}))
        

@user_private_router.callback_query(F.data.startswith('change_lang_'))
async def change_language(call: CallbackQuery):
    user_id = call.from_user.id
    action = call.data.split('_')[2]    

    await call.message.delete()
    if action in ['uz', 'ru', 'en']:
        await sync_to_async(UserMod.objects.filter(user_id=user_id).update)(language=action)
        lang = languages[action]
        await call.message.answer(text=lang['main'], reply_markup=CreateInline({lang['product_btn']:'get_products', 
            lang['set_lang']:'set_language', lang['info']:'get_information'}, just=(1, 2)))
    elif action == 'back':
        lang = await get_user_language(user_id)
        await call.message.answer(text=lang['main'], reply_markup=CreateInline({lang['product_btn']:'get_products', 
            lang['set_lang']:'set_language', lang['info']:'get_information'}, just=(1, 2)))


@user_private_router.message(lambda message: message.text in ['🔙 Back', '🔙 Назад', '🔙 Orqaga'])
async def get_back(message: Message):
        user_id = message.from_user.id
        lang = await get_user_language(user_id)
        await message.answer(text=lang['main'], reply_markup=CreateInline({lang['product_btn']:'get_products', 
            lang['set_lang']:'set_language', lang['info']:'get_information'}, just=(1, 2)))
