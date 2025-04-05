from aiogram import Router, html
from aiogram.filters import Command
from aiogram.types import Message

from bot.keyboard.inline import markup_start
from bot.keyboard.reply import rmk
from bot.text import HELLO_TEXT, MENU_TEXT
from aiogram.fsm.context import FSMContext
from log.log import setup_logger

router = Router()
logger = setup_logger("Cancel")

@router.message(Command('cancel'))
async def cancel_creation(message: Message, state: FSMContext):
    await message.answer(text='⚡️ Действие отменено', reply_markup=rmk)
    user_name = message.chat.first_name
    await message.answer(
        text=f"{HELLO_TEXT}{html.bold(user_name)}!{MENU_TEXT}",
        reply_markup=markup_start
    )
    await state.clear()
    return