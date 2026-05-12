import asyncio
from fastapi import FastAPI
from bot import dp, bot

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ok"}


@app.on_event("startup")
async def startup():
    asyncio.create_task(start_bot())


async def start_bot():
    while True:
        try:
            print("BOT STARTED")

            await dp.start_polling(
                bot,
                skip_updates=True
            )

        except Exception as e:
            print(f"BOT CRASH: {e}")

            await asyncio.sleep(5)