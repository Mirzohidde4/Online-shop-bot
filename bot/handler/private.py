import django, os
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from asgiref.sync import sync_to_async
from main.models import UserMod, CategoryMod, ProductMod, BasketMod
from ..settings.states import UserState
from ..settings.buttons import CreateInline, Createreply
from ..settings.languages import languages
from ..settings.functions import *


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
        reply_markup=get_main_button(lang=lang))


@user_private_router.callback_query(F.data == 'get_products')
async def get_categorys(call: CallbackQuery):
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
        await call.message.answer(text=lang['lang_changed'], reply_markup=ReplyKeyboardRemove())
        await call.message.answer(text=lang['main'], reply_markup=get_main_button(lang=lang))
    elif action == 'back':
        lang = await get_user_language(user_id)
        await call.message.answer(text=lang['main'], reply_markup=get_main_button(lang=lang))


@user_private_router.message(lambda message: message.text in ['🔙 Back', '🔙 Назад', '🔙 Orqaga'])
async def get_back(message: Message):
    user_id = message.from_user.id
    lang = await get_user_language(user_id)
    await message.answer(text=lang['main'], reply_markup=get_main_button(lang=lang))


@user_private_router.message(F.text)
async def get_products(message: Message):
    category = message.text
    user_id = message.from_user.id
    user_filter = await sync_to_async(UserMod.objects.filter(user_id=user_id).first)()

    if user_filter.language == 'uz':
        category_filter = await sync_to_async(CategoryMod.objects.filter(name_uz=category).first)()
    if user_filter.language == 'ru':
        category_filter = await sync_to_async(CategoryMod.objects.filter(name_ru=category).first)()
    if user_filter.language == 'en':
        category_filter = await sync_to_async(CategoryMod.objects.filter(name_en=category).first)()
    
    await send_products_by_category(bot=message.bot, chat_id=user_id, category_id=category_filter.id, page=1, lang=user_filter.language)


@user_private_router.callback_query(lambda c: c.data.startswith("category_"))
async def pagination_callback(call: CallbackQuery):
    action = call.data.split("_")
    category_id = int(action[1])
    user_filter = await sync_to_async(UserMod.objects.filter(user_id=call.from_user.id).first)()

    if action[2] == 'addbasket':
        try:
            product = await sync_to_async(ProductMod.objects.get)(name=action[3], price=action[4])
            await sync_to_async(BasketMod.objects.create)(user=call.from_user.id, product=product, category=category_id, count=1)
            await call.message.answer(f"{product.name} savatchaga qo'shildi!")
        
        except ProductMod.DoesNotExist:
            await call.message.answer("Mahsulot topilmadi. Iltimos, ma'lumotlarni tekshiring.")
        except Exception as e:
            await call.message.answer(f"Xatolik yuz berdi: {str(e)}")

    elif action[2] == 'page':
        page = int(action[3])
        await send_products_by_category(call.message.bot, call.from_user.id, category_id, page, call.message.message_id, user_filter.language)

    elif action[2] == 'back':
        await call.message.delete()
        lang = languages[user_filter.language]
        await call.message.answer(text=lang['main'], reply_markup=get_main_button(lang=lang))



@user_private_router.callback_query(F.data == 'get_basket')
async def get_basket(call: CallbackQuery):
    user_id = call.from_user.id
    user_filter = await sync_to_async(UserMod.objects.filter(user_id=user_id).first)()

    await call.message.delete()
    await send_products_by_user(bot=call.message.bot, chat_id=user_id, page=1, lang=user_filter.language)


@user_private_router.callback_query(F.data.startswith('basket_'))
async def pagination_basket(call: CallbackQuery):
    action = call.data.split("_")   
    chat_id = int(action[1])
    user_filter = await sync_to_async(UserMod.objects.filter(user_id=chat_id).first)()

    if action[2] == 'page':
        page = int(action[3])
        await send_products_by_user(bot=call.message.bot, chat_id=chat_id, page=page, message_id=call.message.message_id, lang=user_filter.language) 