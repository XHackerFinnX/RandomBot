from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request

router = APIRouter(
    prefix="",
    tags=["AllGive"]
)

templates = Jinja2Templates(directory="templates")

@router.get('/allgive', response_class=HTMLResponse)
async def main_random(request: Request):
    return templates.TemplateResponse("allgive.html", {"request": request})