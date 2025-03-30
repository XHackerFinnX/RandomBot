from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from db.models.user import select_raffle_active_my, select_raffle_completed_my, select_raffle_expectation_my

router = APIRouter(
    prefix="",
    tags=["AllGive"]
)

class MyRaffle(BaseModel):
    user_id: int

templates = Jinja2Templates(directory="templates")

@router.get('/allgive', response_class=HTMLResponse)
async def main_random(request: Request):
    return templates.TemplateResponse("allgive.html", {"request": request})

@router.post('/api/raffle-my')
async def my_raffle(data: MyRaffle, status: str):
    user_id = data.user_id
    if status == 'active':
        data_raffle = await select_raffle_active_my(user_id)
    elif status == 'pending':
        data_raffle = await select_raffle_expectation_my(user_id)
    elif status == 'completed':
        data_raffle = await select_raffle_completed_my(user_id)
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
    
    return JSONResponse(content=data_raffle)