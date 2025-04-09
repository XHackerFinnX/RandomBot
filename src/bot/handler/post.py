import aiohttp
from aiogram import Router, html
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboard.inline import markup_start, markup_save_post
from bot.keyboard.reply import rmk
from bot.utils.states import Post
from bot.text import HELLO_TEXT, MENU_TEXT
from db.models.posts import add_post
from log.log import setup_logger
from zoneinfo import ZoneInfo
from datetime import datetime

router = Router()
MOSCOW_TZ = ZoneInfo("Europe/Moscow")
logger = setup_logger("Post")

@router.message(Command('newpost'))
async def start_newpost(message: Message, state: FSMContext):
    user_name = message.chat.first_name
    user_id = message.chat.id
    logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) Запустил команду /newpost")
    await state.set_state(Post.text_post)
    await message.answer(text='💬 Отправьте мне ваш пост (текст или фото с подписью) \nДля отмены нажмите 👉🏻 /cancel')

@router.message(Post.text_post)
async def text_post_newpost(message: Message, state: FSMContext):

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
        logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) Отменил действие командой /start находясь в /newpost")
        await state.clear()
        return

    post_text = message.text if message.text else ""
    photo_id = None
    
    if message.photo:
        if not message.caption:
            logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) отправил фотографию без текста")
            await message.answer("🙂 Вы не ввели описание поста.\n\nДля отмены нажмите 👉🏻 /cancel")
            return
        photo_id = message.photo[-1].file_id
        post_text = message.caption
    
    await state.update_data(text_post=post_text, photo_id=photo_id)
    await state.set_state(Post.confirmation)

    if photo_id:
        logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) отправил пост с фотографией")
        sent_message = await message.answer_photo(photo=photo_id, caption=post_text, reply_markup=markup_save_post)
    else:
        logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) отправил пост без фотографии")
        sent_message = await message.answer(text=post_text, reply_markup=markup_save_post)
        
    await state.update_data(confirm_message_id=sent_message.message_id)
        

@router.callback_query(lambda c: c.data == "accept_post")
async def save_post(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()

    text_post = data.get("text_post", "")
    photo_id = data.get("photo_id")
    date_post = datetime.now(MOSCOW_TZ).replace(tzinfo=None)

    photo_bytes = None
    if photo_id:
        photo_bytes = await download_photo(photo_id, callback.bot)

    success = await add_post(user_id, text_post, photo_bytes, date_post)
    if success:
        logger.info(f"Пользователь ID:({user_id}) создал и сохранил пост")
        await callback.message.answer("🎉 Пост создан и сохранен", reply_markup=markup_start)
        confirm_message_id = data.get("confirm_message_id")
        if confirm_message_id:
            try:
                await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=confirm_message_id)
            except Exception as e:
                logger.warning(f"Пользователь ID:({user_id}) ошибка при удалении сообщения при сохранение поста: {e}")
                print(f"Ошибка при удалении сообщения: {e}")
    else:
        logger.warning(f"Пользователь ID:({user_id}) ошибка при сохранении поста.")
        await callback.message.answer("⚠ Ошибка при сохранении поста.")

    await state.clear()
    
@router.callback_query(lambda c: c.data == "cancel_post")
async def cancel_post(callback: CallbackQuery, state: FSMContext):
    TEXT_CANCEL = "❌ Создание поста отменено. \n\nВы можете создать новый пост 👉🏻 /newpost"
    user_id = callback.from_user.id
    logger.info(f"Пользователь ID:({user_id}) отменил создание поста")
    await callback.message.answer(text=TEXT_CANCEL, reply_markup=markup_start)
    data = await state.get_data()
    confirm_message_id = data.get("confirm_message_id")
    if confirm_message_id:
        try:
            await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=confirm_message_id)
        except Exception as e:
            logger.warning(f"Пользователь ID:({user_id}) ошибка при удалении сообщения при отмены поста: {e}")
    await state.clear()
    
async def download_photo(photo_id: str, bot) -> bytes:
    file = await bot.get_file(photo_id)
    file_path = file.file_path

    url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()