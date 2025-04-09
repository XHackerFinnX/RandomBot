import base64
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import APIRouter, Request, BackgroundTasks
from pydantic import BaseModel
from fastapi.responses import RedirectResponse

from db.models.channels import check_channel_id_sub, select_channel, delete_channel_user, select_channel_true
from db.models.posts import select_post, delete_post_user, select_view_post_user
from log.log import setup_logger
from bot.handler.message import (message_post, message_channel_delete,
                                 message_post_delete, message_channel_update, message_add_newpost,
                                 message_add_newchannel)
from config import config
from typing import Optional

from db.models.user import check_user_save_raffle, select_channel_save_raffle

router = APIRouter(
    prefix="",
    tags=["Basic"]
)

templates = Jinja2Templates(directory="templates")
logger = setup_logger("Basic")

class GetDataRequest(BaseModel):
    user_id: int

class ReqData(BaseModel):
    user_id: int


@router.get("/", response_class=HTMLResponse)
async def main_random(request: Request, tgWebAppStartParam: Optional[str] = None):
    if tgWebAppStartParam:
        redirect_url = f"{config.WEBAPP_URL}/raffle?raffle_id={tgWebAppStartParam}"
        return RedirectResponse(url=redirect_url)

    return templates.TemplateResponse("basic.html", {"request": request})

@router.post("/api/get_data")
async def get_data(request: GetDataRequest):
    user_id = request.user_id
    data_channel = await select_channel(user_id)
    data_post = await select_post(user_id)
    channels = []
    posts = []
    for data_user in data_channel:
        if data_user['channel_photo'] is None:
            user_photo = None
        else:
            user_photo = f"data:image/png;base64,{base64.b64encode(data_user['channel_photo']).decode('utf-8')}"
        channels.append(
            {
                "id": data_user['channel_id'],
                "name": data_user['channel_name'],
                "subscribers": data_user['channel_subscribers'],
                "photo_url": user_photo
            }
        )
        
    for data_user in data_post:
        posts.append(
            {
                "id": data_user['id'],
                "title": data_user['text_post'],
                "date": data_user['date_post']
            }
        )
    return {
        "channels": [ch for ch in channels],
        "posts": [pt for pt in posts]
    }

@router.post("/api/get_posts")
async def get_posts(request: GetDataRequest):
    user_id = request.user_id
    data_post = await select_post(user_id)
    posts = []
    for data_user in data_post:
        posts.append(
            {
                "id": data_user['id'],
                "title": data_user['text_post'],
                "date": data_user['date_post'],
                "user_id": data_user['user_id']
            }
        )
        
    return [pt for pt in posts]

@router.post("/api/get_channel/all")
async def get_posts(request: GetDataRequest):
    user_id = request.user_id
    data_channel = await select_channel(user_id)
    channels = []
    for data_user in data_channel:
        if data_user['channel_photo'] is None:
            user_photo = None
        else:
            user_photo = f"data:image/png;base64,{base64.b64encode(data_user['channel_photo']).decode('utf-8')}"
        channels.append(
            {
                "id": data_user['channel_id'],
                "name": data_user['channel_name'],
                "subscribers": data_user['channel_subscribers'],
                "photo_url": user_photo,
                "verified": data_user['channel_status'],
                "user_id": data_user['user_id']
            }
        )
        
    return [pt for pt in channels]

@router.post("/api/get_channel")
async def get_posts(request: GetDataRequest):
    user_id = request.user_id
    data_channel = await select_channel_true(user_id)
    if await check_user_save_raffle(user_id):
        data_channel_sub = await select_channel_save_raffle(user_id)
        if data_channel_sub['sub_channel_id']:
            # data_channel = []
            channel_id_list = []
            for id_c in data_channel:
                channel_id_list.append(id_c['channel_id'])
                
            for id_channel_sub in data_channel_sub['sub_channel_id']:
                if id_channel_sub not in channel_id_list:
                    data_channel += await check_channel_id_sub(id_channel_sub)

    channels = []
    for data_user in data_channel:
        if data_user['channel_photo'] is None:
            user_photo = None
        else:
            user_photo = f"data:image/png;base64,{base64.b64encode(data_user['channel_photo']).decode('utf-8')}"
        channels.append(
            {
                "id": data_user['channel_id'],
                "name": data_user['channel_name'],
                "subscribers": data_user['channel_subscribers'],
                "photo_url": user_photo,
                "verified": data_user['channel_status'],
                "user_id": data_user['user_id']
            }
        )
        
    return [pt for pt in channels]

@router.post("/api/update-channel")
async def update_channel(user_id: int, channelid: int, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(message_channel_update, user_id, channelid)
        return {"ok": True}
    except:
        return JSONResponse(
            status_code=400,
            content={"status": "error"}
        )


@router.post("/api/delete-channel")
async def delete_channel(user_id: int, channelid: int, background_tasks: BackgroundTasks):
    try:
        await delete_channel_user(user_id, channelid)
        background_tasks.add_task(message_channel_delete, user_id, channelid)
    except:
        pass
    
    return {"ok": True}

@router.post("/api/view-post")
async def view_post(user_id: int, postid: int, background_tasks: BackgroundTasks):
    try:
        text_post = await select_view_post_user(postid, user_id)
        background_tasks.add_task(message_post, user_id, text_post)
        return {"ok": True}
    except:
        return JSONResponse(
            status_code=400,
            content={"status": "error"}
        )


@router.post("/api/delete-post")
async def delete_post(user_id: int, postid: int, background_tasks: BackgroundTasks):
    try:
        await delete_post_user(postid, user_id)
        background_tasks.add_task(message_post_delete, user_id)
    except:
        pass
    
    return {"ok": True}
        
@router.post("/api/new_post")
async def new_post_add(data: ReqData, background_tasks: BackgroundTasks):
    background_tasks.add_task(message_add_newpost, data.user_id)
    return {"ok": "post"}
    
@router.post("/api/new_channel")
async def new_channel_add(data: ReqData, background_tasks: BackgroundTasks):
    background_tasks.add_task(message_add_newchannel, data.user_id)
    return {"ok": "channel"}

@router.post("/api/new_post/mobile")
async def new_post_add():
    return {"new": "post"}
    
@router.post("/api/new_channel/mobile")
async def new_channel_add():
    return {"new": "channel"}
    
@router.get('/loading')
async def loading_raffle(request: Request):
    return templates.TemplateResponse("loading.html", {"request": request})