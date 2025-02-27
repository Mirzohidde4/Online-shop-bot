from asgiref.sync import sync_to_async
from main.models import *
from ..settings.languages import languages
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InputMediaPhoto, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from config.settings import PAGE_SIZE
from bot.settings.buttons import CreateInline, Createreply


async def get_admin():
    admin_filter = await sync_to_async(list)(AdminMod.objects.all())
    return admin_filter[0] if admin_filter else None


def get_main_button(lang):
    return CreateInline({
        lang['product_btn']:'get_products', lang['set_lang']:f"set_language", 
        lang['my_basket']:'get_basket', lang['info']:'get_information'}, just=(1, 2, 1) )


async def get_product(lang, user_filter):
    category_filter = await sync_to_async(list, thread_sensitive=True)(CategoryMod.objects.all())

    if user_filter.language == 'uz':
        markup = Createreply(*(i.name_uz for i in category_filter), lang['back'])
    elif user_filter.language == 'ru':    
        markup = Createreply(*(i.name_ru for i in category_filter), lang['back'])
    elif user_filter.language == 'en':    
        markup = Createreply(*(i.name_en for i in category_filter), lang['back'])
    return markup


async def get_user_language(user_id: int) -> str:
    user_filter = await sync_to_async(UserMod.objects.filter(user_id=user_id).first)()
    return languages[user_filter.language] if user_filter else languages['uz']


async def get_products_by_category(category_id):
    category_filter = await sync_to_async(CategoryMod.objects.filter(id=category_id).first)()
    products = await sync_to_async(list)(ProductMod.objects.filter(category_id=category_filter.id).all())
    return products


def paginate_products(products, page):
    start = (int(page) - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    return products[start:end]


def create_pagination_keyboard(category_id, page, has_next, name, price, chat_id, soni=1, lang='uz', product_id=None):
    language = languages[lang]
    start, end = 0, 0
    keyboard = InlineKeyboardBuilder()
    has_next = True if str(has_next).lower() == 'true' else False

    if category_id:
        keyboard.row(
            InlineKeyboardButton(text="➖", callback_data=f"cat_{category_id}_updt_mns_{page}_{soni}_{has_next}_{name}_{price}_{product_id}"),
            InlineKeyboardButton(text=f"{soni}", callback_data="noop"),
            InlineKeyboardButton(text="➕", callback_data=f"cat_{category_id}_updt_pls_{page}_{soni}_{has_next}_{name}_{price}_{product_id}")
        )
        if int(page) > 1:
            keyboard.add(InlineKeyboardButton(text=language['previous_pg'], callback_data=f"cat_{category_id}_page_{int(page) - 1}")) 
        else: start = 1 
        if has_next:
            keyboard.add(InlineKeyboardButton(text=language['next_pg'], callback_data=f"cat_{category_id}_page_{int(page) + 1}"))
        else: end = 1

        keyboard.add(InlineKeyboardButton(text=language['set_basket'], callback_data=f"cat_{category_id}_add_{product_id}_{soni}"))
        keyboard.add(InlineKeyboardButton(text=language['back'], callback_data=f"cat_{category_id}_back"))
        keyboard.adjust(3, 2, 2) if (start == 1 and end == 1) or (start == 0 and end == 0) else keyboard.adjust(3, 1, 2)
   
    else:
        if int(page) > 1:
            keyboard.add(InlineKeyboardButton(text=language['previous_pg'], callback_data=f"basket_{chat_id}_page_{int(page) - 1}")) 
        else: start = 1 
        if has_next:
            keyboard.add(InlineKeyboardButton(text=language['next_pg'], callback_data=f"basket_{chat_id}_page_{int(page) + 1}"))
        else: 
            end = 1
        piece = True if (start == 1 and end == 1) else False
        
        keyboard.add(InlineKeyboardButton(text=language['order'], callback_data=f"basket_{chat_id}_order_{product_id}_{piece}"))
        keyboard.add(InlineKeyboardButton(text=language['delete'], callback_data=f"basket_{chat_id}_delete_{product_id}_{piece}"))
        keyboard.add(InlineKeyboardButton(text=language['back'], callback_data=f"basket_{chat_id}_back"))
        keyboard.adjust(2, 2) if (start == 1 and end == 1) or (start == 0 and end == 0) else keyboard.adjust(1, 2)
    return keyboard.as_markup()


async def send_products_by_category(bot: Bot, chat_id, category_id, page, message_id=None, lang='uz', call=None):
    products = await get_products_by_category(category_id)
    paginated_products = paginate_products(products, page)
    
    if not products or len(products) == 0:
        if call: await bot.answer_callback_query(callback_query_id=call.id, text=languages[lang]['none_category'], show_alert=True)
        else: await bot.send_message(chat_id=chat_id, text=languages[lang]['none_category'])
        return 

    for product in paginated_products:
        text = f"Nomi: {product.name}\nNarxi: {product.price} so'm\n\n" if lang == 'uz' else \
               f"Название: {product.name}\nЦена: {product.price} сум\n\n" if lang == 'ru' else \
               f"Name: {product.name}\nPrice: {product.price} sum\n\n"
        media = FSInputFile(path=product.photo.path)

        has_next = len(products) > int(page) * PAGE_SIZE
        keyboard = create_pagination_keyboard(category_id, page, has_next, product.name, product.price, chat_id=chat_id, lang=lang, product_id=product.pk)
        
        try:
            if message_id:
                await bot.edit_message_media(media=InputMediaPhoto(media=media, caption=text), 
                    chat_id=chat_id, message_id=message_id, reply_markup=keyboard)
            else: await bot.send_photo(chat_id=chat_id, photo=media, caption=text, reply_markup=keyboard)
        except TelegramBadRequest as e:
            if "Message is not modified" not in str(e): raise


async def send_products_by_user(bot: Bot, chat_id, page, message_id=None, lang='uz', call=None):
    products = await sync_to_async(list)(BasketMod.objects.filter(user=chat_id).select_related('product'))
    paginated_products = paginate_products(products, page)

    if not products or len(products) == 0:
        await bot.answer_callback_query(callback_query_id=call.id, text=languages[lang]['none_basket'], show_alert=True)
        return 
    if message_id is None: await call.message.delete()
    
    for product in paginated_products:
        if not product.product: continue

        text = f"Nomi: {product.product.name}\nNarxi: {product.product.price} so'm\nMiqdori: {product.count} {languages[lang]['quantity']}\n\n" if lang == 'uz' else \
               f"Название: {product.product.name}\nЦена: {product.product.price} сум\nКоличество: {product.count} {languages[lang]['quantity']}\n\n" if lang == 'ru' else \
               f"Name: {product.product.name}\nPrice: {product.product.price} som\nAmount: {product.count} {languages[lang]['quantity']}\n\n"
        media = FSInputFile(path=product.product.photo.path)

        has_next = len(products) > page * PAGE_SIZE
        keyboard = create_pagination_keyboard(None, page, has_next, product.product.name, product.product.price, chat_id=chat_id, lang=lang, product_id=product.product.pk)

        try:
            if message_id:
                await bot.edit_message_media(media=InputMediaPhoto(media=media, caption=text),
                    chat_id=chat_id, message_id=message_id, reply_markup=keyboard)
            else: await bot.send_photo(chat_id=chat_id, photo=media, caption=text, reply_markup=keyboard)
        except TelegramBadRequest as e:
            if "Message is not modified" not in str(e): raise


async def get_discount(price):
    discount = await sync_to_async(DiscountMod.objects.first, thread_sensitive=True)()
    discount_price = price 

    if discount and int(price) > discount.discount_price:
        percent = int(price) * discount.discount_percent / 100    
        discount_price = int(price) - percent

    return f"<i><del>{price}</del></i>  <b>{'%.2f' % discount_price}</b>" if discount_price != price else f"<b>{'%.2f' % price}</b>"
