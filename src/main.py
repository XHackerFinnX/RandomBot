import asyncio
import uvicorn

from config import config
from contextlib import asynccontextmanager

from bot.handler import commands, post, channel, cancel
from bot.handler.raffle_time import background_task
from router.basic import router as router_basic
from router.newgive import router as router_newgive
from router.allgive import router as router_allgive
from router.raffle import router as router_raffle

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

bot = Bot(
    config.BOT_TOKEN.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Список для хранения задач
tasks = []

def is_event_loop_running():
    try:
        loop = asyncio.get_event_loop()
        return loop.is_running()
    except RuntimeError:
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(
        url=f"{config.WEBHOOK_URL}{config.WEBHOOK_PATH}",
        drop_pending_updates=True,
        allowed_updates=dp.resolve_used_update_types()
    )

    task = asyncio.create_task(background_task())
    tasks.append(task)

    try:
        yield
    except asyncio.CancelledError:
        print("Приложение завершает работу.")
    finally:
        await bot.session.close()

        if is_event_loop_running():
            for task in tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    print("Таски отменены.")
        else:
            print("Цикл обработки событий замкнут, никаких задач для отмены нет.")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router_basic)
app.include_router(router_newgive)
app.include_router(router_allgive)
app.include_router(router_raffle)

dp.include_routers(
    cancel.router,
    post.router,
    channel.router,
    commands.router
)

@app.post(config.WEBHOOK_PATH)
async def webhooks(request: Request):
    update = Update.model_validate(
        await request.json(),
        context={'bot': bot}
    )
    await dp.feed_update(bot, update)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return True

if __name__ == "__main__":
    uvicorn.run(app, host=config.APP_HOST, port=config.APP_PORT, ssl_keyfile="/etc/letsencrypt/live/racerandom.ru/privkey.pem", ssl_certfile="/etc/letsencrypt/live/racerandom.ru/fullchain.pem")