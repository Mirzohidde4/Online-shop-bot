from asgiref.sync import sync_to_async
from main.models import UserMod, ProductMod, CategoryMod, BasketMod
from ..settings.languages import languages
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InputMediaPhoto, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from config.settings import PAGE_SIZE
from bot.settings.buttons import CreateInline


def get_main_button(lang):
    return CreateInline(
        {
            lang['product_btn']:'get_products', lang['set_lang']:f"set_language", 
            lang['my_basket']:'get_basket', lang['info']:'get_information'
        }, just=(1, 2, 1) )


async def get_user_language(user_id: int) -> str:
    user_filter = await sync_to_async(UserMod.objects.filter(user_id=user_id).first)()
    return languages[user_filter.language] if user_filter else languages['uz']


async def get_products_by_category(category_id):
    category_filter = await sync_to_async(CategoryMod.objects.filter(id=category_id).first)()
    products = await sync_to_async(list)(ProductMod.objects.filter(category_id=category_filter.id).all())
    return products


def paginate_products(products, page):
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    return products[start:end]


def create_pagination_keyboard(category_id, page, has_next, name, price, chat_id, lang='uz'):
    language = languages[lang]
    start, end = 0, 0
    keyboard = InlineKeyboardBuilder()

    if category_id:
        if page > 1:
            keyboard.add(InlineKeyboardButton(text=language['previous_pg'], callback_data=f"category_{category_id}_page_{page - 1}")) 
        else:
            start = 1 
        if has_next:
            keyboard.add(InlineKeyboardButton(text=language['next_pg'], callback_data=f"category_{category_id}_page_{page + 1}"))
        else:
            end = 1
        keyboard.add(InlineKeyboardButton(text=language['set_basket'], callback_data=f"category_{category_id}_addbasket_{name}_{price}"))
   
    else:
        if page > 1:
            keyboard.add(InlineKeyboardButton(text=language['previous_pg'], callback_data=f"basket_{chat_id}_page_{page - 1}")) 
        else:
            start = 1 
        if has_next:
            keyboard.add(InlineKeyboardButton(text=language['next_pg'], callback_data=f"basket_{chat_id}_page_{page + 1}"))
        else:
            end = 1
        keyboard.add(InlineKeyboardButton(text=language['order'], callback_data=f"basket_{chat_id}_order_{name}_{price}"))

    keyboard.adjust(2, 2) if (start == 1 and end == 1) or (start == 0 and end == 0) else keyboard.adjust(1, 2)
    return keyboard.as_markup()


async def send_products_by_category(bot: Bot, chat_id, category_id, page, message_id=None, lang='uz'):
    products = await get_products_by_category(category_id)
    paginated_products = paginate_products(products, page)
    
    if products is None or len(products) == 0:
        await bot.send_message(chat_id=chat_id, text=languages[lang]['none_category'])
        return None
    
    for product in paginated_products:
        if lang == 'uz':
            text = "".join(f"Nomi: {product.name}\nNarxi: {product.price} so'm\n\n")
        elif lang == 'ru':
            text = "".join(f"Название: {product.name}\nЦена: {product.price} сум\n\n")
        elif lang == 'en':
            text = "".join(f"Name: {product.name}\nPrice: {product.price} som\n\n")
        
        media = FSInputFile(path=product.photo.path)

        has_next = len(products) > page * PAGE_SIZE
        keyboard = create_pagination_keyboard(category_id, page, has_next, product.name, product.price, chat_id=chat_id, lang=lang)
        
        try:
            if message_id:
                await bot.edit_message_media(media=InputMediaPhoto(media=media, caption=text), chat_id=chat_id, message_id=message_id, reply_markup=keyboard)
            else:
                await bot.send_photo(chat_id=chat_id, photo=media, caption=text, reply_markup=keyboard)
        except TelegramBadRequest as e:
            if "Message is not modified" not in str(e): raise


async def get_product_by_user(user_id):
    return await sync_to_async(list)(BasketMod.objects.filter(user=user_id).select_related('product'))


async def send_products_by_user(bot: Bot, chat_id, page, message_id=None, lang='uz'):
    products = await get_product_by_user(chat_id)
    paginated_products = paginate_products(products, page)

    if not products or len(products) == 0:
        await bot.send_message(chat_id=chat_id, text=languages[lang]['none_category'])
        return None

    for product in paginated_products:
        if not product.product:
            continue

        text = f"Nomi: {product.product.name}\nNarxi: {product.product.price} so'm\n\n" if lang == 'uz' else \
               f"Название: {product.product.name}\nЦена: {product.product.price} сум\n\n" if lang == 'ru' else \
               f"Name: {product.product.name}\nPrice: {product.product.price} som\n\n"

        media = FSInputFile(path=product.product.photo.path)

        has_next = len(products) > page * PAGE_SIZE
        keyboard = create_pagination_keyboard(None, page, has_next, product.product.name, product.product.price, chat_id=chat_id, lang=lang)

        try:
            if message_id:
                await bot.edit_message_media(
                    media=InputMediaPhoto(media=media, caption=text),
                    chat_id=chat_id, 
                    message_id=message_id,
                    reply_markup=keyboard
)
            else:
                await bot.send_photo(chat_id=chat_id, photo=media, caption=text, reply_markup=keyboard)
        except TelegramBadRequest as e:
            if "Message is not modified" not in str(e):
                raise
