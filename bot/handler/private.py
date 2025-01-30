import django, os
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from asgiref.sync import sync_to_async
from main.models import UserMod, CategoryMod, ProductMod, BasketMod
from ..settings.states import PhoneNumber
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
    lang = await get_user_language(user_id)
    user_filter = await sync_to_async(UserMod.objects.filter(user_id=user_id).first)()
    
    if not user_filter:
        txt = f"{languages['uz']['select_lang']}\n\n{languages['ru']['select_lang']}\n\n{languages['en']['select_lang']}"
        await message.answer(text=txt, 
            reply_markup=CreateInline({'🇺🇿 O\'zbek': 'language_uz', '🇷🇺 Русский': 'language_ru', '🇬🇧 English': 'language_en'}))
    else:
        await message.answer(text=lang['start'].replace('full_name', full_name), 
            reply_markup=get_main_button(lang=lang))


@user_private_router.callback_query(F.data.startswith('language_'))
async def select_language(call: CallbackQuery, state: FSMContext):
    action = call.data.split('_')[1]
    if action in ['uz', 'ru', 'en']: await state.update_data({'language': action})
    await call.message.delete()
    await call.message.answer(text=languages[action]['contact_text'], reply_markup=Createreply(languages[action]['contact'], contact=True))
    await state.set_state(PhoneNumber.number)


@user_private_router.message(PhoneNumber.number)
async def send_phone(message: Message, state: FSMContext):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    data = await state.get_data()
    language = data.get('language')
    
    if message.contact and message.contact.phone_number:
        await sync_to_async(UserMod.objects.create)(user_id=user_id, user_name=username, 
            full_name=full_name, language=language, phone=message.contact.phone_number)
        await state.clear()
        await message.answer(text=languages[language]['start'].replace('full_name', full_name), 
            reply_markup=get_main_button(lang=languages[language]))
    else: 
        await message.answer(text=languages[language]['contact_text'], reply_markup=Createreply(languages[language]['contact'], contact=True))  


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


@user_private_router.callback_query(lambda c: c.data.startswith("cat_"))
async def pagination_callback(call: CallbackQuery):
    action = call.data.split("_")
    category_id = int(action[1])
    user_filter = await sync_to_async(UserMod.objects.filter(user_id=call.from_user.id).first)()
    lang = languages[user_filter.language]
    
    if action[2] == 'add':
        try:
            count = int(action[4])
            product = await sync_to_async(ProductMod.objects.get)(id=action[3])
            product_filter = await sync_to_async(BasketMod.objects.filter(user=call.from_user.id, product=product.pk, category=category_id).first)()
            if product_filter:
                old_count = product_filter.count
                new_count = int(old_count) + int(count)
                try:
                    await sync_to_async(BasketMod.objects.filter(user=call.from_user.id, product=product.pk, category=category_id).update)(count=new_count)
                except Exception as error:
                    print(f"mahsulot yangilashda xatolik: {str(error)}")    
            else:  
                await sync_to_async(BasketMod.objects.create)(user=call.from_user.id, product=product, category=category_id, count=count)
            await call.answer(lang['add_done'].replace('name', product.name), show_alert=True)
        
        except ProductMod.DoesNotExist:
            print("Mahsulot tugagan.")
        except Exception as e:
            print(f"Xatolik yuz berdi: {str(e)}")

    elif action[2] == "updt":
        page = action[4]
        has_next = action[6]
        name = action[7]
        price = action[8]
        product_id = action[9]
        current_count = int(action[5])
        
        situation = False
        if action[3] == "pls": 
            current_count += 1
            situation = True
        elif action[3] == "mns":
            if current_count > 1: 
                current_count -= 1
                situation = True
            else: await call.answer(text=lang['ban_cnt'])

        keyboard = create_pagination_keyboard(
            category_id=category_id, page=page, has_next=has_next, name=name, price=price, 
            chat_id=call.from_user.id, soni=current_count, lang=user_filter.language, product_id=product_id)     
        
        if situation: await call.message.edit_reply_markup(reply_markup=keyboard)   

    elif action[2] == 'page':
        page = int(action[3])
        await send_products_by_category(call.message.bot, call.from_user.id, category_id, page, call.message.message_id, user_filter.language, call=call)

    elif action[2] == 'back':
        await call.message.delete()
        lang = languages[user_filter.language]
        await call.message.answer(text=lang['main'], reply_markup=get_main_button(lang=lang))


@user_private_router.callback_query(F.data == 'get_basket')
async def get_basket(call: CallbackQuery):
    user_id = call.from_user.id
    user_filter = await sync_to_async(UserMod.objects.filter(user_id=user_id).first)()
    await send_products_by_user(bot=call.message.bot, chat_id=user_id, page=1, lang=user_filter.language, call=call)


@user_private_router.callback_query(F.data.startswith('basket_'))
async def pagination_basket(call: CallbackQuery, state: FSMContext):
    action = call.data.split("_")   
    chat_id = int(action[1])
    user_filter = await sync_to_async(UserMod.objects.filter(user_id=chat_id).first)()
    lang = languages[user_filter.language]

    if action[2] == 'page':
        page = int(action[3])
        await send_products_by_user(bot=call.message.bot, chat_id=chat_id, page=page, message_id=call.message.message_id, lang=user_filter.language, call=call) 

    elif action[2] == 'back':
        await call.message.delete()
        await call.message.answer(text=lang['main'], reply_markup=get_main_button(lang=lang))

    elif action[2] == 'delete':
        product_id = int(action[3])
        try:
            await sync_to_async(BasketMod.objects.filter(user=chat_id, product=product_id).delete)()
            await call.answer(text=lang['delete_done'])
            
            if action[4] == 'True':
                await call.message.delete()
                await call.message.answer(text=lang['main'], reply_markup=get_main_button(lang=lang))
            elif action[4] == 'False':
                await send_products_by_user(bot=call.message.bot, chat_id=chat_id, page=1, lang=user_filter.language, call=call) 
        except Exception as error:
            print('o\'chirishda xatolik:', error)    

    elif action[2] == 'order':
        await call.message.delete()
        if action[4] == 'True':
            await state.update_data({'chat_id': chat_id, 'product_id': int(action[3])})
            await call.message.answer(text=lang['location_txt'], reply_markup=Createreply(lang['get_location'], location=True))
            await state.set_state(PhoneNumber.location)
        elif action[4] == 'False':
            # await call.message.answer(text)
            print('many')    


@user_private_router.message(PhoneNumber.location)
async def get_location(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data['chat_id']
    product_id = data.get('product_id')
    if message.location:
        pass