from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from config import config

markup_start = (
    InlineKeyboardBuilder().button(
        text="🎲 Начать",
        web_app=WebAppInfo(url=config.WEBAPP_URL)
    )
).as_markup()

markup_continue = (
    InlineKeyboardBuilder().button(
        text="🎲 Открыть приложение",
        web_app=WebAppInfo(url=config.WEBAPP_URL)
    )
).as_markup()

markup_save_post = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='✅ Сохранить', callback_data='accept_post'),
            InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_post')
        ]
    ]
)