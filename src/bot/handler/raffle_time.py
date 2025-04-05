import asyncio
import random

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from db.models.user import (
    add_raffle_archive,
    select_all_user_raffle,
    select_raffle_data,
    select_turn_user_raffle,
    update_raffle_end,
)

from datetime import datetime
from zoneinfo import ZoneInfo
from config import config
from bot.handler.message import (
    message_channel_result_raffle,
    message_data_check_sub_user_end_raffle,
    message_new_raffle,
    message_new_raffle_list_data,
    message_update_raffle_end,
)
from db.models.channels import check_channel_id_sub, select_active_raffle
from log.log import setup_logger

bot = Bot(
    config.BOT_TOKEN.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
MOSCOW_TZ = ZoneInfo("Europe/Moscow")
logger = setup_logger("Commands")
# Хранилище для задач
raffle_tasks = []


async def background_task():
    
    raffle = await select_active_raffle(status='Активен')
    for raffle_start in raffle:
        task = asyncio.create_task(
            waiting_drawing(
                raffle_start["raffle_id"],
                raffle_start["start_date"],
                raffle_start["end_date"],
            )
        )
        raffle_tasks.append(task)
    
    raffle_expectation = await select_active_raffle(status='Ожидание')
    for raffle_start_expectation in raffle_expectation:
        data = await select_raffle_data(raffle_start_expectation["raffle_id"])
        task = asyncio.create_task(
            waiting_drawing_start(
                data,
                raffle_start_expectation["raffle_id"],
                raffle_start_expectation["start_date"],
                raffle_start_expectation["end_date"],
            )
        )
        raffle_tasks.append(task)


async def waiting_drawing(hash_id, start_date, end_date):
    try:
        entry_date = datetime.now(MOSCOW_TZ).replace(tzinfo=None)
        raffle_time = (end_date - entry_date).total_seconds()
        print(f"Розыгрыш {hash_id} закончится через {raffle_time} сек.")
        if raffle_time > 0:
            await asyncio.sleep(raffle_time)
        else:
            await asyncio.sleep(2)

        data = await select_raffle_data(hash_id)
        if data[0]["status"] == 'Завершен' or data[0]["status"] == 'Отмена':
            print('Розыгрыш завершен принудительно!')
            return
        
        await update_raffle_end(hash_id, "Ждем")
        await asyncio.sleep(2)
        
        count_winner = data[0]["user_winners"]
        sub_channel = data[0]["sub_channel_id"]

        all_user = await select_all_user_raffle(hash_id)

        list_winner = []
        if not all_user:
            pass
        else:
            for user in all_user:
                all_sub = []
                for data_user in sub_channel:
                    data_channel = await check_channel_id_sub(int(data_user))

                    if not data_channel:
                        continue

                    status_sub = await message_data_check_sub_user_end_raffle(
                        user["user_id"],
                        {
                            "channel_id": data_channel[0]["channel_id"],
                            "channel_tg": data_channel[0]["channel_tg"],
                        },
                    )
                    all_sub.append(status_sub)
                if all(all_sub):
                    list_winner.append(user["user_id"])

        turn_list_winner = []
        if count_winner >= len(list_winner):
            turn_list_winner.extend(list_winner)
        else:
            turn_user = await select_turn_user_raffle(hash_id)
            for tlw in turn_user:
                turn_list_winner.append(tlw["user_id"])

            for _ in range(count_winner):
                if count_winner == len(turn_list_winner):
                    break
                winner_user = random.choice(list_winner)
                turn_list_winner.append(winner_user)
                list_winner.remove(winner_user)

        text_post = data[0]["post_text"]
        await message_update_raffle_end(text_post, hash_id)
        await add_raffle_archive(hash_id, turn_list_winner, start_date, end_date)
        await message_channel_result_raffle(hash_id, turn_list_winner)
        await update_raffle_end(hash_id, "Завершен")
    except asyncio.CancelledError:
        print(f"Розыгрыш {hash_id} отключен! И временно не работает")


async def waiting_drawing_start(data, hash_id, start_date, end_date):
    try:
        entry_date = datetime.now(MOSCOW_TZ).replace(tzinfo=None)
        raffle_time_start = (start_date - entry_date).total_seconds()

        print(f"Розыгрыш {hash_id} начнется через {raffle_time_start} сек.")
        if raffle_time_start > 0:
            await asyncio.sleep(raffle_time_start)
        else:
            await asyncio.sleep(2)
        
        temp_data = await select_raffle_data(hash_id)
        
        if temp_data[0]["status"] == "Активен" or temp_data[0]["status"] == 'Отмена':
            print('Розыгрыш завершен принудительно из статуса ожидание!')
            return
        
        await update_raffle_end(hash_id, "Активен")
        if type(data) is list:
            await message_new_raffle_list_data(data, hash_id)
        else:
            await message_new_raffle(data, hash_id)
            
        entry_date = datetime.now(MOSCOW_TZ).replace(tzinfo=None)
        raffle_time = (end_date - entry_date).total_seconds()
        print(f"Розыгрыш {hash_id} закончится через {raffle_time} сек.")
        if raffle_time > 0:
            await asyncio.sleep(raffle_time)
        else:
            await asyncio.sleep(2)

        await update_raffle_end(hash_id, "Ждем")
        await asyncio.sleep(2)
        data = await select_raffle_data(hash_id)
        count_winner = data[0]["user_winners"]
        sub_channel = data[0]["sub_channel_id"]

        all_user = await select_all_user_raffle(hash_id)

        list_winner = []
        if not all_user:
            pass
        else:
            for user in all_user:
                all_sub = []
                for data_user in sub_channel:
                    data_channel = await check_channel_id_sub(int(data_user))

                    if not data_channel:
                        continue

                    status_sub = await message_data_check_sub_user_end_raffle(
                        user["user_id"],
                        {
                            "channel_id": data_channel[0]["channel_id"],
                            "channel_tg": data_channel[0]["channel_tg"],
                        },
                    )
                    all_sub.append(status_sub)
                if all(all_sub):
                    list_winner.append(user["user_id"])

        turn_list_winner = []
        if count_winner >= len(list_winner):
            turn_list_winner.extend(list_winner)
        else:
            turn_user = await select_turn_user_raffle(hash_id)
            for tlw in turn_user:
                turn_list_winner.append(tlw["user_id"])

            for _ in range(count_winner):
                if count_winner == len(turn_list_winner):
                    break
                winner_user = random.choice(list_winner)
                turn_list_winner.append(winner_user)
                list_winner.remove(winner_user)

        text_post = data[0]["post_text"]
        await message_update_raffle_end(text_post, hash_id)
        await add_raffle_archive(hash_id, turn_list_winner, start_date, end_date)
        await message_channel_result_raffle(hash_id, turn_list_winner)
        await update_raffle_end(hash_id, "Завершен")
    except asyncio.CancelledError:
        print(f"Розыгрыш {hash_id} отключен! И временно не работает")
