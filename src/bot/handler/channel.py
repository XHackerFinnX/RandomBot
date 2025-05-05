import requests
from aiogram import Router, html, Bot
from aiogram.filters import Command
from aiogram.types import Message, ChatMemberAdministrator, FSInputFile
from aiogram.fsm.context import FSMContext
from bot.keyboard.inline import markup_start
from bot.keyboard.reply import rmk, add_channel_keyboard
from bot.utils.states import Channel
from bot.text import HELLO_TEXT, MENU_TEXT, ADD_CHANNEL_TEXT
from db.models.channels import check_channel, add_channel, update_channel
from log.log import setup_logger
from config import config

router = Router()
logger = setup_logger("Channel")

@router.message(Command('newchannel'))
async def start_channel(message: Message, state: FSMContext):
    photo = FSInputFile(r"src/bot/photo/channel_bot.jpg")
    user_name = message.chat.first_name
    user_id = message.chat.id
    logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) Запустил команду /newchannel")
    await state.set_state(Channel.channel)
    await message.answer_photo(
        photo=photo,
        caption=ADD_CHANNEL_TEXT,
        reply_markup=add_channel_keyboard
    )


@router.message(Channel.channel)
async def receive_channel(message: Message, state: FSMContext, bot: Bot):
    
    user_name = message.chat.first_name
    user_id = message.chat.id
    
    if message.text == "/start":
        await message.answer(
            text='⚡️ Действие отменено',
            reply_markup=rmk
        )
        await message.answer(
            text=f"{HELLO_TEXT}{html.bold(user_name)}!{MENU_TEXT}",
            reply_markup=markup_start
        )
        logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) Отменил действие командой /start находясь в /newchannel")
        await state.clear()
        return
    
    try:
        channel_id = message.chat_shared.chat_id
        await message.answer(text='🔍 Проверяем канал...')
        logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) Проверяем канал channel_id: {channel_id}")
        bot_member = await message.bot.get_chat_member(channel_id, bot.id)
        if isinstance(bot_member, ChatMemberAdministrator):
            chat = await bot.get_chat(channel_id)

            try:
                member_count = await bot.get_chat_member_count(channel_id)
                logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) Проверяем канал channel_id: {channel_id} и получаем количество подписчиков: {member_count}")
            except Exception as e:
                logger.warning(f"Пользователь ID:({user_id}) Name:({user_name}) Проверяем канал channel_id: {channel_id} и ошибка в получении количества подписчиков")
                member_count = 0
            
            try:
                if chat.photo:
                    file = await bot.get_file(chat.photo.big_file_id)
                    file_path = file.file_path
                    photo_url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN.get_secret_value()}/{file_path}"

                    response = requests.get(photo_url)
                    if response.status_code == 200:
                        photo_bytes = response.content
                        logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) Проверяем канал channel_id: {channel_id} и получаем аватар канала с фотографией")
                    else:
                        logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) Проверяем канал channel_id: {channel_id} и получаем аватар канала без фотографии. response.status_code = {response.status_code}.")
                        photo_bytes = None
                else:
                    logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) Проверяем канал channel_id: {channel_id} и получаем аватар канала без фотографии")
                    photo_bytes = None
                    
            except Exception as e:
                logger.warning(f"Пользователь ID:({user_id}) Name:({user_name}) Проверяем канал channel_id: {channel_id} и не удалось получить аватарку ошибка при скачивании фото: {e}")

            if not await check_channel(user_id, channel_id):
                logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) Канал channel_id: {channel_id} успешно прошел проверку и добавлен в БД")
                await add_channel(user_id, channel_id, member_count, chat.title, photo_bytes, "@"+chat.username)
                await message.answer(f"✅ Канал успешно добавлен! Бот имеет доступ для управления этим каналом.", reply_markup=rmk)
                await state.clear()
            else:
                logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) Канал channel_id: {channel_id} успешно прошел проверку и данные обновлены в БД")
                await update_channel(user_id, channel_id, member_count, chat.title, photo_bytes, True, "@"+chat.username)
                await message.answer(f"🙂 Канал уже добавлен.\n\nВы можете добавить другой канал.\n\nДля отмены нажмите 👉🏻 /cancel")
        else:
            logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) Channel_id: {channel_id} Пользователь не является АДМИНОМ канала или он является закрытым")
            await message.answer("❌ Бот не является администратором этого канала. Пожалуйста, добавьте бота в канал с правами администратора. Или сделайте его публичным!\n\nНажмите 👉🏻 /cancel и попробуйте добавить канал снова!")

    except:
        logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) Ошибка при добавлении канала")
        await message.answer("❌ Бот не является администратором этого канала. Пожалуйста, добавьте бота в канал с правами администратора. Или сделайте его публичным!\n\nНажмите 👉🏻 /cancel и попробуйте добавить канал снова!")