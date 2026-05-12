import asyncio
from fastapi import FastAPI
from bot import main

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok"}

@app.on_event("startup")
async def startup():
    asyncio.create_task(main())