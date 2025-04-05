import requests
from aiogram import Router, html, Bot
from aiogram.filters import Command
from aiogram.types import Message, ChatMemberAdministrator
from aiogram.fsm.context import FSMContext
from config import config

from bot.keyboard.inline import markup_start
from bot.keyboard.reply import rmk, add_channel_keyboard
from bot.utils.states import Channel
from bot.text import HELLO_TEXT, MENU_TEXT, ADD_CHANNEL_TEXT
from log.log import setup_logger
from db.models.channels import check_channel, add_channel, update_channel

router = Router()
logger = setup_logger("Channel")

@router.message(Command('newchannel'))
async def start_channel(message: Message, state: FSMContext):
    await state.set_state(Channel.channel)
    await message.answer(text=ADD_CHANNEL_TEXT, reply_markup=add_channel_keyboard)


@router.message(Channel.channel)
async def receive_channel(message: Message, state: FSMContext, bot: Bot):
    
    if message.text == "/start":
        await message.answer(text='⚡️ Действие отменено', reply_markup=rmk)
        user_name = message.chat.first_name
        await message.answer(
            text=f"{HELLO_TEXT}{html.bold(user_name)}!{MENU_TEXT}",
            reply_markup=markup_start
        )
        await state.clear()
        return
    
    try:
        await message.answer(text='🔍 Проверяем канал...')
        channel_id = message.chat_shared.chat_id
        user_id = message.chat.id

        bot_member = await message.bot.get_chat_member(channel_id, bot.id)
        if isinstance(bot_member, ChatMemberAdministrator):
            chat = await bot.get_chat(channel_id)

            try:
                member_count = await bot.get_chat_member_count(channel_id)
            except Exception as e:
                member_count = 0
            
            try:
                if chat.photo:
                    file = await bot.get_file(chat.photo.big_file_id)
                    file_path = file.file_path
                    photo_url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN.get_secret_value()}/{file_path}"

                    response = requests.get(photo_url)
                    if response.status_code == 200:
                        photo_bytes = response.content
                    else:
                        print("Ошибка при скачивании фото.")
                        photo_bytes = None
                else:
                    print("У канала нет фото.")
                    photo_bytes = None
                    
            except Exception as e:
                photo_url = f"Не удалось получить аватарку: {e}"
        
            if not await check_channel(user_id, channel_id):
                await add_channel(user_id, channel_id, member_count, chat.title, photo_bytes, "@"+chat.username)
                await message.answer(f"✅ Канал успешно добавлен! Бот имеет доступ для управления этим каналом.", reply_markup=rmk)
                await state.clear()
            else:
                await update_channel(user_id, channel_id, member_count, chat.title, photo_bytes, True, "@"+chat.username)
                await message.answer(f"🙂 Канал уже добавлен.\n\nВы можете добавить другой канал.\n\nДля отмены нажмите 👉🏻 /cancel")
        else:
            await message.answer("❌ Бот не является администратором этого канала. Пожалуйста, добавьте бота в канал с правами администратора.")

    except:
        await message.answer("❌ Бот не является администратором этого канала. Пожалуйста, добавьте бота в канал с правами администратора.")