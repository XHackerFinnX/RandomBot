import base64
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List
from bot.handler.telegram_auth import get_verified_user
from db.models.user import count_user_sub_channel, select_all_raffle_active, select_raffle_data, add_user_raffle, delete_user_raffle, check_user_raffle, select_winner_raffle_archive, winner_user
from db.models.channels import check_channel_id_sub
from log.log import setup_logger
from bot.handler.message import message_check_sub_user, message_check_user_raffle, message_data_check_sub_user, message_update_send_channel, message_check_user_raffle_initdata

from datetime import datetime
from zoneinfo import ZoneInfo

router = APIRouter(prefix="", tags=["Raffle"])

templates = Jinja2Templates(directory="templates")
MOSCOW_TZ = ZoneInfo("Europe/Moscow")
logger = setup_logger("Raffle")


class HashRaffle(BaseModel):
    hashid: str
    userid: int
    
class HashArchive(BaseModel):
    hashid: str
    
class CheckUserSub(BaseModel):
    userId: int
    raffleId: str
    mockChannels: List[dict]

@router.get("/raffle", response_class=HTMLResponse)
async def main_random(raffle_id: str, request: Request):
    data = await select_raffle_data(raffle_id)

    if not data:
        return templates.TemplateResponse("basic.html", {"request": request})

    data = data[0]
    name = data["name"]
    status = data["status"]
    
    data_raffle = []
    raffle_list_active = await select_all_raffle_active()
    count_indicator = len(raffle_list_active)
    for raff_id in raffle_list_active:
        raffle_name = raff_id['name']
        count_user = await count_user_sub_channel(raff_id['raffle_id'])
        raffle_description = raff_id['post_text']
        data_raffle.append(
            {
                'name': raffle_name,
                'description': raffle_description,
                'count': count_user[0]['count'],
                'url': f"/?tgWebAppStartParam={raff_id['raffle_id']}"
            }
        )

    if status == 'Активен' or status == 'Ждем':
        return templates.TemplateResponse(
            "endgive.html",
            {
                "request": request,
                "raffle_id": raffle_id,
                "name": name,
                'data_raffle': data_raffle,
                'count_indicator': count_indicator
            },
        )
        
    elif status == 'Ожидание' or status == 'Отмена':
        return templates.TemplateResponse("basic.html", {"request": request})
    
    elif status == 'Завершен':
        return templates.TemplateResponse(
            "finish.html",
            {
                "request": request,
                "raffle_id": raffle_id,
                "name": name
            },
        )


@router.post("/api/channels-raffle-sub")
async def get_channels(data: HashRaffle, background_tasks: BackgroundTasks, user_data: dict = Depends(get_verified_user)):

    user_id = data.userid
    hash_id = data.hashid
    data = await select_raffle_data(hash_id)
    print(user_data.user)
    background_tasks.add_task(message_check_user_raffle_initdata, user_data.user)
    data = data[0]
    sub_channel = data["sub_channel_id"]
    end_date = data["end_date"]
    text_post = data["post_text"]
    button_post = data['post_button']

    if isinstance(end_date, datetime):
        end_date_iso = end_date.replace(tzinfo=MOSCOW_TZ).isoformat()
    else:
        # Если end_date строка
        end_date_iso = (
            datetime.strptime(str(end_date), "%Y-%m-%d %H:%M:%S")
            .replace(tzinfo=MOSCOW_TZ)
            .isoformat()
        )

    channels = []
    all_sub = []
    for data_user in sub_channel:
        data_channel = await check_channel_id_sub(int(data_user))

        if not data_channel:
            continue

        channels_photo = data_channel[0]["channel_photo"]
        if channels_photo is None:
            user_photo = None
        else:
            user_photo = f"data:image/png;base64,{base64.b64encode(channels_photo).decode('utf-8')}"
        
        status_sub = await message_data_check_sub_user(user_id, {"channel_id": data_channel[0]["channel_id"], "channel_tg": data_channel[0]["channel_tg"]})
        all_sub.append(status_sub)
        
        if all(all_sub):
            if not await check_user_raffle(hash_id, user_id):
                await add_user_raffle(hash_id, user_id)
                background_tasks.add_task(message_update_send_channel, text_post, button_post, hash_id)
        else:
            await delete_user_raffle(hash_id, user_id)
            background_tasks.add_task(message_update_send_channel, text_post, button_post, hash_id)
        
        channels.append(
            {
                "id": data_channel[0]["channel_id"],
                "name": data_channel[0]["channel_name"],
                "photo_url": user_photo,
                "channel_tg": data_channel[0]["channel_tg"],
                "status_sub": status_sub
            }
        )
    return {"data_channel": channels, "end_date": end_date_iso, "all_sub": all(all_sub)}


@router.post('/api/check-subscription-user')
async def check_sub_user(data: CheckUserSub, background_tasks: BackgroundTasks):
    is_subscribed = await message_check_sub_user(data.userId, data.mockChannels)

    hash_id = data.raffleId
    user_id = data.userId
    data = await select_raffle_data(hash_id)
    text_post = data[0]["post_text"]
    button_post = data[0]['post_button']

    if is_subscribed:
        if not await check_user_raffle(hash_id, user_id):
            await add_user_raffle(hash_id, user_id)
            background_tasks.add_task(message_update_send_channel, text_post, button_post, hash_id)
        return {"ok": True, "message": "User is subscribed to at least one channel."}
    else:
        await delete_user_raffle(hash_id, user_id)
        background_tasks.add_task(message_update_send_channel, text_post, button_post, hash_id)
        return {"ok": False, "message": "User is not subscribed to any channel."}
    
@router.post('/api/list_winner')
async def winner_user_list(data: HashArchive):
    
    list_name_winner = await select_winner_raffle_archive(data.hashid)
    if not list_name_winner:
        return []
    list_winner = []
    for i, user_win in enumerate(list_name_winner, 1):
        user_tg = await winner_user(user_win)
        list_winner.append(
            {
                "id": i,
                "name": user_tg
            }
        )
        
    return list_winner