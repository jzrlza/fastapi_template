#import yaml
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi_utils.session import FastAPISessionMaker
from fastapi_utils.tasks import repeat_every
import csv
import re
import time

app = FastAPI()

@app.on_event("startup")
def on_startup():
	print("App is starting up.")


#initialize_databases(sql_file, config)

@app.post("/post_something")
#@repeat_every(seconds=30) #works
async def post_something(request: Request):
	req = await request.json()

	return {"result" : [req]}

app.mount("/", StaticFiles(directory="web"), name="web")
