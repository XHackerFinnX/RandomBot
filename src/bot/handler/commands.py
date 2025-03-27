from aiogram import Bot, Router, html
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboard.inline import markup_start
from bot.keyboard.reply import add_channel_keyboard
from bot.tg_name import telegram_name_users
from db.models.user import check_user, add_user, update_winuser
from bot.text import HELLO_TEXT, MENU_TEXT, ADD_CHANNEL_TEXT
from bot.utils.states import Channel, Post
from aiogram.fsm.context import FSMContext

from zoneinfo import ZoneInfo
from datetime import datetime

router = Router()
MOSCOW_TZ = ZoneInfo("Europe/Moscow")

@router.message(CommandStart())
async def start_bot(message: Message, state: FSMContext, bot: Bot):
    
    await state.clear()
    args = message.text.split(maxsplit=1)
    
    user_data = await telegram_name_users(message)
    user_id = user_data['id_user']
    user_name = user_data['uname']
    user_fname = user_data['fname']
    user_lname = user_data['lname']
    entry_date = datetime.now(MOSCOW_TZ).replace(tzinfo=None)
    
    if not await check_user(user_id):
        await add_user(
            user_id,
            user_name,
            user_fname,
            user_lname,
            entry_date
        )
        
    if len(args) == 1:
        await message.answer(
            text=f"{HELLO_TEXT}{html.bold(user_fname)}!{MENU_TEXT}",
            reply_markup=markup_start
        )
    else:
        await message.delete()
        data = args[-1].split('_')
        if data[-1] == 'channel':
            await state.set_state(Channel.channel)
            await message.answer(text=ADD_CHANNEL_TEXT, reply_markup=add_channel_keyboard)
        
        if data[-1] == 'post':
            await state.set_state(Post.text_post)
            await message.answer(text='💬 Отправьте мне ваш пост (текст или фото с подписью) \nДля отмены нажмите 👉🏻 /cancel')
            
@router.message()
async def start_bot(message: Message, bot: Bot):
    
    if message.text.startswith('/winuser'):
        user_data = await telegram_name_users(message)
        print(user_data)
        data_hash_id = message.text.split("=")
        user_id = user_data['id_user']
        await update_winuser(data_hash_id[-1], user_id)