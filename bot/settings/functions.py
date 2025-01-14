from asgiref.sync import sync_to_async
from main.models import UserMod
from ..settings.languages import languages


async def get_user_language(user_id: int) -> str:
    user_filter = await sync_to_async(UserMod.objects.filter(user_id=user_id).first)()
    return languages[user_filter.language] if user_filter else languages['uz']