from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButtonRequestChat, ChatAdministratorRights, ReplyKeyboardRemove

rmk = ReplyKeyboardRemove()

builder = ReplyKeyboardBuilder()

builder.button(
    text="🗂 Добавить канал",
    request_chat=KeyboardButtonRequestChat(
        request_id=1,
        chat_is_channel=True,
        user_administrator_rights=ChatAdministratorRights(
            is_anonymous=False,
            can_manage_chat=False,  
            can_manage_video_chats=False,  
            can_restrict_members=False,  
            can_promote_members=False,  
            can_change_info=False,  
            can_invite_users=False,  
            can_post_stories=False,  
            can_edit_stories=False,  
            can_delete_stories=False,  
            can_post_messages=True,
            can_edit_messages=True,
            can_delete_messages=True
        ),
        bot_administrator_rights=None
    )
)

add_channel_keyboard = builder.as_markup(resize_keyboard=True, one_time_keyboard=True)