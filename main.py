#import yaml
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi_utils.session import FastAPISessionMaker
from fastapi_utils.tasks import repeat_every
from fastapi.security import OAuth2PasswordRequestForm #auth
import csv
import re
import time
import os
from datetime import timedelta #auth
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
import db.models
from db.database import engine, SessionLocal

from routers import auth, users
from routers.auth import get_current_user, user_not_found_exception, authenticate_user, create_access_token

config = {
    "test": False,
    "data_path": "./data",
    "allow_origins": [],
    "storage": 
            {
                "type": "filesystem",
                "path": "pgdata"
            },
  }

app = FastAPI()

@app.on_event("startup")
def on_startup():
	print("App is starting up.")

db.models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(users.router)

#initialize_databases(sql_file, config)

@app.post("/post_something")
#@repeat_every(seconds=30) #works
async def post_something(request: Request):
	req = await request.json()

	return {"result" : [req]}

app.mount("/", StaticFiles(directory="web"), name="web")
