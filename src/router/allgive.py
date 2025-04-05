import asyncio
import base64
from datetime import datetime
from zoneinfo import ZoneInfo
from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from db.models.user import count_user_sub_channel, select_raffle_active_my, select_raffle_data, select_raffle_participating, select_raffle_completed_my, select_raffle_expectation_my, update_cancel_raffle, update_status_raffle_start
from db.models.channels import check_channel_id_sub
from bot.handler.raffle_time import waiting_drawing
from bot.handler.message import message_new_raffle_list_data
from log.log import setup_logger

router = APIRouter(
    prefix="",
    tags=["AllGive"]
)
MOSCOW_TZ = ZoneInfo("Europe/Moscow")
logger = setup_logger("AllGive")

class MyRaffle(BaseModel):
    user_id: int
    
class RaffleId(BaseModel):
    raffle_id: str
    
class CancelRaffle(BaseModel):
    raffle_id: str
    action: str

templates = Jinja2Templates(directory="templates")

@router.get('/allgive', response_class=HTMLResponse)
async def main_random(request: Request):
    return templates.TemplateResponse("allgive.html", {"request": request})

@router.post('/api/raffle-my')
async def my_raffle(data: MyRaffle, status: str):
    user_id = data.user_id
    if status == 'active':
        data_raffle = await select_raffle_active_my(user_id)
        data_raffle_participating = await select_raffle_participating(user_id, 'Активен')
    elif status == 'pending':
        data_raffle = await select_raffle_expectation_my(user_id)
        data_raffle_participating = await select_raffle_participating(user_id, 'Ожидание')
    elif status == 'completed':
        data_raffle = await select_raffle_completed_my(user_id)
        data_raffle_participating = await select_raffle_participating(user_id, 'Завершен')
    else:
        raise HTTPException(status_code=400, detail="Invalid status")

    if data_raffle is None:
        return JSONResponse(status_code=500, content={"message": "Error fetching data from the database"})

    data_raffle = [{
                "raffle_id": row["raffle_id"],
                "name": row["name"],
                "start_date": row["start_date"].isoformat() if isinstance(row["start_date"], datetime) else str(row["start_date"]),
                "end_date": row["end_date"].isoformat() if isinstance(row["end_date"], datetime) else str(row["end_date"]),
                "status": row["status"]
            } for row in data_raffle]
    
    for row in data_raffle_participating:
        if row["raffle_id"] in [i["raffle_id"] for i in data_raffle]:
            pass
        else:
            data_raffle.append(
                {
                    "raffle_id": row["raffle_id"],
                    "name": row["name"],
                    "start_date": row["start_date"].isoformat() if isinstance(row["start_date"], datetime) else str(row["start_date"]),
                    "end_date": row["end_date"].isoformat() if isinstance(row["end_date"], datetime) else str(row["end_date"]),
                    "status": row["status"],
                    "status_user": "participating"
                }
            )
    
    return JSONResponse(content=data_raffle)

@router.get("/manage-raffle")
async def manage_raffle(raffle_id: str, request: Request):
    return templates.TemplateResponse("settingsgive.html", {
        "request": request,
        "raffle_id": raffle_id
    })
    
@router.post("/api/get_raffle_data_settings")
async def raffle_data_settings(data: RaffleId):

    hash_id = data.raffle_id
    data = await select_raffle_data(hash_id)
    data = data[0]
    
    name = data['name']
    post_text = data['post_text']
    post_button = data['post_button']
    user_winners = data['user_winners']
    status = data['status']
    start_date = data['start_date']
    end_date = data['end_date']
    start_date_iso = start_date.strftime("%d.%m.%Y %H:%M")
    end_date_iso = end_date.strftime("%d.%m.%Y %H:%M")
    
    sub_channels = []
    for sci in data['sub_channel_id']:
        data_channel = await check_channel_id_sub(sci)
        if not data_channel:
            pass
        else:
            data_channel = data_channel[0]
            if data_channel['channel_photo'] is None:
                user_photo = None
            else:
                user_photo = f"data:image/png;base64,{base64.b64encode(data_channel['channel_photo']).decode('utf-8')}"
            sub_channels.append(
                {
                    "id": data_channel['channel_id'],
                    "name": data_channel['channel_name'],
                    "subscribers": data_channel['channel_subscribers'],
                    "photo_url": user_photo,
                    "verified": data_channel['channel_status'],
                    "user_id": data_channel['user_id']
                }
            )
    
    announ_channels = []
    for aci in data['announcet_channel_id']:
        data_channel = await check_channel_id_sub(aci)
        if not data_channel:
            pass
        else:
            data_channel = data_channel[0]
            if data_channel['channel_photo'] is None:
                user_photo = None
            else:
                user_photo = f"data:image/png;base64,{base64.b64encode(data_channel['channel_photo']).decode('utf-8')}"
            announ_channels.append(
                {
                    "id": data_channel['channel_id'],
                    "name": data_channel['channel_name'],
                    "subscribers": data_channel['channel_subscribers'],
                    "photo_url": user_photo,
                    "verified": data_channel['channel_status'],
                    "user_id": data_channel['user_id']
                }
            )
            
    res_channels = []
    for rci in data['announcet_channel_id']:
        data_channel = await check_channel_id_sub(rci)
        if not data_channel:
            pass
        else:
            data_channel = data_channel[0]
            if data_channel['channel_photo'] is None:
                user_photo = None
            else:
                user_photo = f"data:image/png;base64,{base64.b64encode(data_channel['channel_photo']).decode('utf-8')}"
            res_channels.append(
                {
                    "id": data_channel['channel_id'],
                    "name": data_channel['channel_name'],
                    "subscribers": data_channel['channel_subscribers'],
                    "photo_url": user_photo,
                    "verified": data_channel['channel_status'],
                    "user_id": data_channel['user_id']
                }
            )
            
    count_user = await count_user_sub_channel(hash_id)
    count_user = count_user[0]["count"]
    
    return JSONResponse(content={
        "name": name,
        "post_text": post_text,
        "button_text": post_button,
        "start_date": start_date_iso,
        "end_date": end_date_iso,
        "winners_count": user_winners,
        "participants_count": count_user,
        "status": status,
        "subscription_channels": sub_channels,
        "announcement_channels": announ_channels,
        "result_channels": res_channels
    })
    
@router.post('/api/perform_raffle_action')
async def perform_raffle_action(data: CancelRaffle):
    raffle = await select_raffle_data(data.raffle_id)
    
    if data.action == 'end':
        asyncio.create_task(
            waiting_drawing(
                raffle[0]["raffle_id"],
                raffle[0]["end_date"],
                raffle[0]["start_date"]
            )
        )
        await asyncio.sleep(2)
        return JSONResponse(content=True, status_code=200)
    
    if data.action == 'start':
        await message_new_raffle_list_data(raffle, data.raffle_id)
        await update_status_raffle_start(data.raffle_id)
        asyncio.create_task(
            waiting_drawing(
                raffle[0]["raffle_id"],
                raffle[0]["start_date"],
                raffle[0]["end_date"]
            )
        )
        await asyncio.sleep(2)
        return JSONResponse(content=True, status_code=200)
    
    if data.action == 'cancel':
        await update_cancel_raffle(data.raffle_id)
        await asyncio.sleep(2)
        return JSONResponse(content=True, status_code=200)
    
    else:
        return JSONResponse(content={"message": False}, status_code=400)