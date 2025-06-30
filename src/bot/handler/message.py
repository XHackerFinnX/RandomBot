import requests
import ast
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import BufferedInputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatMemberAdministrator,
)
from bot.keyboard.inline import markup_continue
from db.models.channels import (
    check_channel,
    select_send_channel_result,
    update_channel,
    update_channel_false,
    select_tgname_channel,
)
from db.models.user import add_channel_send, add_user, check_user, select_photo_post, select_photo_raffle, update_user, winner_user, select_channel_send, count_user_sub_channel
from log.log import setup_logger
from config import config
from datetime import datetime
from zoneinfo import ZoneInfo

bot = Bot(
    config.BOT_TOKEN.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
MOSCOW_TZ = ZoneInfo("Europe/Moscow")
logger = setup_logger("Message")

async def message_check_user_raffle(user_id):
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f'Попытка {attempt}: Получаем user_id пользователя для bot.get_chat(): {user_id}')
            user_data = await bot.get_chat(user_id)
            user_name = '@' + str(user_data.username)
            user_fname = str(user_data.first_name)
            user_lname = str(user_data.last_name)
            entry_date = datetime.now(MOSCOW_TZ).replace(tzinfo=None)

            if not await check_user(user_id):
                logger.info(f"Добавляем данные нового пользователя user_id {user_id}")
                await add_user(
                    user_id,
                    user_name,
                    user_fname,
                    user_lname,
                    entry_date
                )
            else:
                logger.info(f"Обновляем данные пользователя user_id {user_id}")
                await update_user(
                    user_id,
                    user_name,
                    user_fname,
                    user_lname,
                    entry_date
                )
            return False
        except Exception as error:
            logger.warning(f'Ошибка при get_chat для user_id={user_id}: {type(error).__name__} - {error}')
            if attempt == max_retries:
                logger.error(f'Не удалось выполнить message_check_user_raffle для user_id {user_id} после {max_retries} попыток')
                return True
                
async def message_check_user_raffle_initdata(user_data):
    user_id = user_data.id
    if await message_check_user_raffle(user_id):
        try:
            logger.info(f'Добавляем через initData: {user_id}')
            user_name = '@' + str(user_data.username)
            user_fname = str(user_data.first_name)
            user_lname = str(user_data.last_name)
            entry_date = datetime.now(MOSCOW_TZ).replace(tzinfo=None)

            if not await check_user(user_id):
                logger.info(f"Добавляем данные нового пользователя user_id {user_id}")
                await add_user(
                    user_id,
                    user_name,
                    user_fname,
                    user_lname,
                    entry_date
                )
            else:
                logger.info(f"Обновляем данные пользователя user_id {user_id}")
                await update_user(
                    user_id,
                    user_name,
                    user_fname,
                    user_lname,
                    entry_date
                )
        except Exception as error:
            logger.warning(f'Ошибка через initData для user_id={user_id}: {type(error).__name__} - {error}')
        

async def message_post(user_id: int, text: str):
    photo_post = await select_photo_post(user_id, text)
    if photo_post is None:
        await bot.send_message(user_id, text)
    else:
        photo = BufferedInputFile(photo_post, filename="image.jpg")
        await bot.send_photo(chat_id=user_id, photo=photo, caption=text)
        
    await bot.send_message(user_id, "👆🏻 ваш пост", reply_markup=markup_continue)


async def message_channel_delete(user_id: int, channel_id: int):

    await bot.leave_chat(channel_id)
    await bot.send_message(
        user_id,
        "Бот покинул канал!\n\n Вы всегда сможете его добавить нажав на 👉🏻 /newchannel",
    )


async def message_post_delete(user_id: int):
    await bot.send_message(
        user_id,
        "Вы удалили пост!\n\n Вы всегда сможете его создать новый нажав на 👉🏻 /newpost",
    )


async def message_channel_update(user_id: int, channel_id: int):

    try:
        bot_member = await bot.get_chat_member(channel_id, bot.id)
        if isinstance(bot_member, ChatMemberAdministrator):
            chat = await bot.get_chat(channel_id)

            try:
                member_count = await bot.get_chat_member_count(channel_id)
            except Exception as e:
                member_count = 0

            # Получаем аватарку
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
                await update_channel(
                    user_id,
                    channel_id,
                    member_count,
                    chat.title,
                    photo_bytes,
                    True,
                    "@" + chat.username,
                )

                return
            else:
                await update_channel(
                    user_id,
                    channel_id,
                    member_count,
                    chat.title,
                    photo_bytes,
                    True,
                    "@" + chat.username,
                )

                return
        else:
            await update_channel_false(user_id, channel_id, False)

            return

    except Exception as e:
        print(e)
        await update_channel_false(user_id, channel_id, False)

        return


async def message_add_newchannel(user_id):
    await bot.send_message(
        chat_id=user_id, text="Нажмите чтобы добавить канал \n\n👉🏻 /newchannel"
    )


async def message_add_newpost(user_id):
    await bot.send_message(
        chat_id=user_id, text="Нажмите чтобы добавить пост \n\n👉🏻 /newpost"
    )


async def message_new_raffle(data, hash_id):
    
    user_id = data.user_id
    name = data.name
    post_text = data.post_text
    markup_sub = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=data.post_button + " (0)",
                    url=f"https://t.me/RandomRace_bot?startapp={hash_id}",
                )
            ]
        ]
    )
    text_id = "ID: " + f"{hash_id}"
    photo_post = await select_photo_raffle(hash_id)
    if photo_post is None:
        await bot.send_message(chat_id=user_id, text=post_text, reply_markup=markup_sub)
    else:
        photo = BufferedInputFile(photo_post, filename="image.jpg")
        await bot.send_photo(chat_id=user_id, photo=photo, caption=post_text, reply_markup=markup_sub)
        
    await bot.send_message(
        chat_id=user_id,
        text=f'{text_id}\n\n✅ Ваш розыгрыш "{name}" создан\n\nВы можете управлять им в приложении 👇🏻\n\nДля вызова меню нажмите 👉🏻 /start',
    )

    channel_sub = []
    if photo_post is None:
        for channel in data.announcet_channel_id:
            try:
                channel_tg = await select_tgname_channel(int(channel))
                send_raffle_channel_sub = await bot.send_message(
                    chat_id=channel_tg, text=post_text, reply_markup=markup_sub
                )
                channel_sub.append([send_raffle_channel_sub.message_id, int(channel)])
            except:
                try:
                    send_raffle_channel_sub = await bot.send_message(
                        chat_id=str(channel), text=post_text, reply_markup=markup_sub
                    )
                    channel_sub.append([send_raffle_channel_sub.message_id, int(channel)])
                except:
                    try:
                        send_raffle_channel_sub = await bot.send_message(
                            chat_id=channel, text=post_text, reply_markup=markup_sub
                        )
                        channel_sub.append(
                            [send_raffle_channel_sub.message_id, int(channel)]
                        )
                    except Exception as e:
                        print(e)
    else:
        photo = BufferedInputFile(photo_post, filename="image.jpg")
        for channel in data.announcet_channel_id:
            try:
                channel_tg = await select_tgname_channel(int(channel))
                send_raffle_channel_sub = await bot.send_photo(
                    chat_id=channel_tg, photo=photo, caption=post_text, reply_markup=markup_sub
                )
                channel_sub.append([send_raffle_channel_sub.message_id, int(channel)])
            except:
                try:
                    send_raffle_channel_sub = await bot.send_photo(
                        chat_id=channel_tg, photo=photo, caption=post_text, reply_markup=markup_sub
                    )
                    channel_sub.append([send_raffle_channel_sub.message_id, int(channel)])
                except:
                    try:
                        send_raffle_channel_sub = await bot.send_photo(
                            chat_id=channel_tg, photo=photo, caption=post_text, reply_markup=markup_sub
                        )
                        channel_sub.append(
                            [send_raffle_channel_sub.message_id, int(channel)]
                        )
                    except Exception as e:
                        print(e)

    await add_channel_send(hash_id, str(channel_sub))
    

async def message_new_raffle_list_data(data, hash_id):
    
    user_id = data[0]["user_id"]
    name = data[0]["name"]
    post_text = data[0]["post_text"]
    markup_sub = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=data[0]["post_button"] + " (0)",
                    url=f"https://t.me/RandomRace_bot?startapp={hash_id}",
                )
            ]
        ]
    )
    text_id = "ID: " + f"{hash_id}"
    photo_post = await select_photo_raffle(hash_id)
    if photo_post is None:
        await bot.send_message(chat_id=user_id, text=post_text, reply_markup=markup_sub)
    else:
        photo = BufferedInputFile(photo_post, filename="image.jpg")
        await bot.send_photo(chat_id=user_id, photo=photo, caption=post_text, reply_markup=markup_sub)
        
    await bot.send_message(
        chat_id=user_id,
        text=f'{text_id}\n\n✅ Ваш розыгрыш "{name}" создан\n\nВы можете управлять им в приложении 👇🏻\n\nДля вызова меню нажмите 👉🏻 /start',
    )

    channel_sub = []
    if photo_post is None:
        for channel in data[0]["announcet_channel_id"]:
            try:
                channel_tg = await select_tgname_channel(int(channel))
                send_raffle_channel_sub = await bot.send_message(
                    chat_id=channel_tg, text=post_text, reply_markup=markup_sub
                )
                channel_sub.append([send_raffle_channel_sub.message_id, int(channel)])
            except:
                try:
                    send_raffle_channel_sub = await bot.send_message(
                        chat_id=str(channel), text=post_text, reply_markup=markup_sub
                    )
                    channel_sub.append([send_raffle_channel_sub.message_id, int(channel)])
                except:
                    try:
                        send_raffle_channel_sub = await bot.send_message(
                            chat_id=channel, text=post_text, reply_markup=markup_sub
                        )
                        channel_sub.append(
                            [send_raffle_channel_sub.message_id, int(channel)]
                        )
                    except Exception as e:
                        print(e)
    else:
        photo = BufferedInputFile(photo_post, filename="image.jpg")
        for channel in data[0]["announcet_channel_id"]:
            try:
                channel_tg = await select_tgname_channel(int(channel))
                send_raffle_channel_sub = await bot.send_photo(
                    chat_id=channel_tg, photo=photo, caption=post_text, reply_markup=markup_sub
                )
                channel_sub.append([send_raffle_channel_sub.message_id, int(channel)])
            except:
                try:
                    send_raffle_channel_sub = await bot.send_photo(
                        chat_id=channel_tg, photo=photo, caption=post_text, reply_markup=markup_sub
                    )
                    channel_sub.append([send_raffle_channel_sub.message_id, int(channel)])
                except:
                    try:
                        send_raffle_channel_sub = await bot.send_photo(
                            chat_id=channel_tg, photo=photo, caption=post_text, reply_markup=markup_sub
                        )
                        channel_sub.append(
                            [send_raffle_channel_sub.message_id, int(channel)]
                        )
                    except Exception as e:
                        print(e)

    await add_channel_send(hash_id, str(channel_sub))


async def message_check_sub_user(user_id, channel_list):

    try:
        is_flag = False
        for cl in channel_list:
            try:
                chat_member = await bot.get_chat_member(cl["channel_tg"], user_id)
            except:
                try:
                    chat_member = await bot.get_chat_member(cl["channel_id"], user_id)
                except:
                    is_flag = False
                    break

            try:
                if chat_member.status in ["member", "administrator", "creator"]:
                    is_flag = True
                else:
                    is_flag = False
                    break
            except:
                is_flag = False
                break

    except Exception as e:
        is_flag = False
        print(f"Error: {e}")

    return is_flag


async def message_data_check_sub_user(user_id, channel_list):
    try:
        chat_member = await bot.get_chat_member(channel_list["channel_tg"], user_id)
    except:
        try:
            chat_member = await bot.get_chat_member(channel_list["channel_id"], user_id)
        except:
            pass

    try:
        if chat_member.status in ["member", "administrator", "creator"]:
            return True
        else:
            return False
    except:
        return False
    
    
async def message_data_check_sub_user_end_raffle(user_id, channel_list):
    try:
        chat_member = await bot.get_chat_member(channel_list["channel_tg"], user_id)
    except:
        try:
            chat_member = await bot.get_chat_member(channel_list["channel_id"], user_id)
        except:
            pass

    try:
        if chat_member.status in ["member", "administrator", "creator"]:
            return True
        else:
            return False
    except:
        return False


async def message_update_send_channel(text_post, button_post, hash_id):

    try:
        channel_list = await select_channel_send(hash_id)
        count_user = await count_user_sub_channel(hash_id)
        count_user = count_user[0]["count"]
        channel_list = ast.literal_eval(channel_list[0]["channel_send"])

        markup_sub = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=button_post + f" ({count_user})",
                        url=f"https://t.me/RandomRace_bot?startapp={hash_id}",
                    )
                ]
            ]
        )

        photo_post = await select_photo_raffle(hash_id)

        if photo_post is None:
            for item in list(channel_list):
                send_id, channel_id = item
                try:
                    await bot.edit_message_text(
                        chat_id=channel_id,
                        message_id=send_id,
                        text=text_post,
                        reply_markup=markup_sub
                    )
                except:
                    print("Не обновлен без фото", item)
        else:
            for item in list(channel_list):
                send_id, channel_id = item
                try:
                    await bot.edit_message_caption(
                        chat_id=channel_id,
                        message_id=send_id,
                        caption=text_post,
                        reply_markup=markup_sub
                    )
                except:
                    print("Не обновлен с фото", item)
    except Exception as e:
        print("Ошибка одновления смс", e)

    return


async def message_update_raffle_end(text_post, hash_id):

    try:
        channel_list = await select_channel_send(hash_id)
        count_user = await count_user_sub_channel(hash_id)
        count_user = count_user[0]["count"]
        channel_list = ast.literal_eval(channel_list[0]["channel_send"])

        markup_sub = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Результаты" + f" ({count_user})",
                        url=f"https://t.me/RandomRace_bot?startapp={hash_id}",
                    )
                ]
            ]
        )

        for item in list(channel_list):
            send_id, channel_id = item
            try:
                await bot.edit_message_text(
                    chat_id=channel_id,
                    message_id=send_id,
                    text=text_post,
                    reply_markup=markup_sub,
                )
            except:
                print("Не обновлен без фото", item)
                try:
                    await bot.edit_message_caption(
                        chat_id=channel_id,
                        message_id=send_id,
                        caption=text_post,
                        reply_markup=markup_sub
                    )
                except:
                    print("Не обновлен с фото", item)
    except Exception as e:
        print("Ошибка одновления смс", e)

    return

async def message_channel_result_raffle(hash_id, turn_list_winner):
    list_result_channel = await select_send_channel_result(hash_id)
    
    text_user_win = ''
    for i, user_id in enumerate(turn_list_winner, 1):
        user_tg = await winner_user(user_id)
        text_user_win += f"{i}. {user_tg}\n"
    
    url_raffle = f"https://t.me/RandomRace_bot?startapp={hash_id}"
    text_result = f'🎉 Розыгрыш завершен!\n\n🏆 Победители:\n{text_user_win}\n\n🔍<a href="{url_raffle}">Проверить результаты</a>'
    for channel_result in list_result_channel:
        await bot.send_message(
            chat_id=channel_result,
            text=text_result,
            parse_mode='HTML'
        )