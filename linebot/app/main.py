from fastapi import FastAPI
from app.routers import linebot
from app.db.database import engine
from app.models import user

user.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Hello World"}


app.include_router(linebot.router)
