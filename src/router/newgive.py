import asyncio
import base64
import hashlib
import random
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import APIRouter, Request, BackgroundTasks, Body
from pydantic import BaseModel
from typing import List

from datetime import datetime
from zoneinfo import ZoneInfo
from db.models.channels import check_channel_user_sub
from db.models.user import add_raffle, add_save_raffle, check_hash_id_raffle, check_user_save_raffle, delete_save_raffle, select_all_save_raffle, update_save_raffle, update_save_raffle_end_date
from log.log import setup_logger
from bot.handler.message import message_new_raffle
from bot.handler.raffle_time import waiting_drawing, waiting_drawing_start

router = APIRouter(prefix="", tags=["NewGive"])

templates = Jinja2Templates(directory="templates")
MOSCOW_TZ = ZoneInfo("Europe/Moscow")
logger = setup_logger("NewGive")

class NameChannel(BaseModel):
    name: str

class UserId(BaseModel):
    user_id: int

class Raffle(BaseModel):
    user_id: int
    name: str
    post_id: int
    post_text: str
    post_button: str
    sub_channel_id: List[int]
    announcet_channel_id: List[int]
    results_channel_id: List[int]
    start_date: str
    end_date: str
    user_win: int
    
class SaveRaffle(BaseModel):
    giveawayData: dict
    step: int


@router.get("/newgive", response_class=HTMLResponse)
async def main_random(request: Request):
    return templates.TemplateResponse("newgive.html", {"request": request})


@router.post("/api/add_channel_sub")
async def add_channel_sub(date: NameChannel):
    data_channel = await check_channel_user_sub(date.name)

    if not data_channel:
        return JSONResponse(status_code=400, content={"status": "error"})

    channels = []
    for data_user in data_channel:
        if data_user["channel_photo"] is None:
            user_photo = None
        else:
            user_photo = f"data:image/png;base64,{base64.b64encode(data_user['channel_photo']).decode('utf-8')}"
        channels.append(
            {
                "id": data_user["channel_id"],
                "name": data_user["channel_name"],
                "subscribers": data_user["channel_subscribers"],
                "photo_url": user_photo,
                "verified": data_user["channel_status"],
                "user_id": data_user["user_id"],
            }
        )

    return channels[0]


async def generate_hash_id(
    user_id: int, name: str, post_id: int, post_text: str
) -> str:
    data = f"{user_id}:{name}:{post_id}:{post_text}:{random.randint(1, 100000)}"

    hash_full = hashlib.sha256(data.encode("utf-8")).hexdigest()
    hash_id = f"{hash_full[:8]}-{hash_full[8:16]}-{hash_full[16:24]}-{hash_full[24:32]}"

    return hash_id


@router.post("/api/create_raffle")
async def create_raffle(data: Raffle, background_tasks: BackgroundTasks):
    await asyncio.sleep(3)
    try:
        hash_id = await generate_hash_id(
            data.user_id, data.name, data.post_id, data.post_text
        )

        if not await check_hash_id_raffle(hash_id):
            pass
        else:
            return JSONResponse(status_code=400, content={"status": "error"})
        
        try:
            start_date_raffle = datetime.strptime(data.start_date, '%d.%m.%Y %H:%M:%S')
        except:
            start_date_raffle = datetime.strptime(data.start_date, '%d.%m.%Y %H:%M')
            
        end_date_raffle = datetime.strptime(data.end_date, '%d.%m.%Y %H:%M')
        if start_date_raffle >= end_date_raffle:
            return JSONResponse(status_code=400, content={"status": "error"})
        
        entry_date = datetime.now(MOSCOW_TZ).replace(tzinfo=None)

        if start_date_raffle > entry_date:
            status = "Ожидание"
        else:
            status = "Активен"

        await delete_save_raffle(data.user_id)
        
        await add_raffle(
            hash_id,
            data.user_id,
            data.name,
            data.post_id,
            data.post_text,
            data.post_button,
            data.sub_channel_id,
            data.announcet_channel_id,
            data.results_channel_id,
            start_date_raffle,
            end_date_raffle,
            data.user_win,
            status,
        )
        if status == "Ожидание":
            background_tasks.add_task(waiting_drawing_start, data, hash_id, start_date_raffle, end_date_raffle)
        else:
            background_tasks.add_task(message_new_raffle, data, hash_id)
            background_tasks.add_task(waiting_drawing, hash_id, start_date_raffle, end_date_raffle)
        return {"ok"}
    except:
        return JSONResponse(status_code=400, content={"status": "error"})


@router.post("/api/save-giveaway")
async def save_create_raffle(data: SaveRaffle):
    try:
        raffle_data = data.giveawayData
        step = data.step

        user_id = raffle_data['user_id']
        name = raffle_data['name']
        post_id = int(raffle_data['post_id'])
        post_text = raffle_data['post_text']
        post_button = raffle_data['post_button']
        sub_channel_id = raffle_data['sub_channel_id']
        announcet_channel_id = raffle_data['announcet_channel_id']
        results_channel_id = raffle_data['results_channel_id']
        
        try:
            start_date_raffle = datetime.strptime(raffle_data['start_date'], '%d.%m.%Y %H:%M:%S')
        except:
            try:
                start_date_raffle = datetime.strptime(raffle_data['start_date'], '%d.%m.%Y %H:%M')
            except:
                start_date_raffle = datetime.strptime(raffle_data['start_date'], '%Y-%m-%dT%H:%M:%S')
        
        try:
            end_date_raffle = datetime.strptime(raffle_data['end_date'], '%d.%m.%Y %H:%M')
        except:
            end_date_raffle = None

        user_win = raffle_data['user_win']
        
        if await check_user_save_raffle(user_id):
            if end_date_raffle is None:
                await update_save_raffle_end_date(
                    user_id,
                    name,
                    post_id,
                    post_text,
                    post_button,
                    sub_channel_id,
                    announcet_channel_id,
                    results_channel_id,
                    start_date_raffle,
                    user_win,
                    step
                )
            else:
                await update_save_raffle(
                    user_id,
                    name,
                    post_id,
                    post_text,
                    post_button,
                    sub_channel_id,
                    announcet_channel_id,
                    results_channel_id,
                    start_date_raffle,
                    end_date_raffle,
                    user_win,
                    step
                )
        else:
            await add_save_raffle(
                user_id,
                name,
                post_id,
                post_text,
                post_button,
                sub_channel_id,
                announcet_channel_id,
                results_channel_id,
                start_date_raffle,
                end_date_raffle,
                user_win,
                step
            )
    except:
        pass
        

@router.post('/api/get-save-raffle')
async def get_save_raffle(data_user: UserId):
    data = await select_all_save_raffle(data_user.user_id)
    try:
        data.update({
            "start_date": data['start_date'].strftime('%d.%m.%Y %H:%M')
        })
    except:
        pass
    
    try:
        data.update({
            "end_date": data['end_date'].strftime('%d.%m.%Y %H:%M')
        })
    except:
        pass
    
    return data

@router.post('/api/delete-save-raffle')
async def delete_save_raffle_back(data: UserId):
    await delete_save_raffle(data.user_id)