from aiogram import Router, html
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.keyboard.inline import markup_start
from bot.keyboard.reply import rmk
from bot.text import HELLO_TEXT, MENU_TEXT
from log.log import setup_logger

router = Router()
logger = setup_logger("Cancel")

@router.message(Command('cancel'))
async def cancel_creation(message: Message, state: FSMContext):
    user_name = message.chat.first_name
    user_id = message.chat.id
    await message.answer(
        text='⚡️ Действие отменено',
        reply_markup=rmk
    )
    await message.answer(
        text=f"{HELLO_TEXT}{html.bold(user_name)}!{MENU_TEXT}",
        reply_markup=markup_start
    )
    logger.info(f"Пользователь ID:({user_id}) Name:({user_name}) Отменил действие командой /cancel")
    await state.clear()
    return