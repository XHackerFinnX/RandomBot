from aiogram import Router, html
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from bot.keyboard.inline import markup_start
from bot.keyboard.reply import add_channel_keyboard
from bot.tg_name import telegram_name_users
from bot.text import HELLO_TEXT, MENU_TEXT, ADD_CHANNEL_TEXT
from bot.utils.states import Channel, Post
from log.log import setup_logger
from zoneinfo import ZoneInfo

from bot.handler.message import message_check_user_raffle

router = Router()
MOSCOW_TZ = ZoneInfo("Europe/Moscow")
logger = setup_logger("Commands")

@router.message(CommandStart())
async def start_bot(message: Message, state: FSMContext):
    
    await state.clear()
    args = message.text.split(maxsplit=1)
    
    user_data = await telegram_name_users(message)
    user_id = user_data['id_user']
    user_name = user_data['uname']
    user_fname = user_data['fname']
    
    await message_check_user_raffle(user_id)
        
    if len(args) == 1:
        logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) Запустил команду /start без параметров")
        await message.answer(
            text=f"{HELLO_TEXT}{html.bold(user_fname)}!{MENU_TEXT}",
            reply_markup=markup_start
        )
    else:
        await message.delete()
        data = args[-1].split('_')
        logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) Запустил команду /start с параметром {data[-1]}")
        if data[-1] == 'channel':
            photo = FSInputFile(r"src/bot/photo/channel_bot.jpg")
            await state.set_state(Channel.channel)
            await message.answer_photo(
                photo=photo,
                caption=ADD_CHANNEL_TEXT,
                reply_markup=add_channel_keyboard
            )
        
        if data[-1] == 'post':
            await state.set_state(Post.text_post)
            await message.answer(text='💬 Отправьте мне ваш пост (текст или фото с подписью) \nДля отмены нажмите 👉🏻 /cancel')