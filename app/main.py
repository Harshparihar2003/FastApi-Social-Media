from fastapi import FastAPI, Response, status, HTTPException, Depends
# from fastapi.params import Body
# from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from random import randrange
# import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .database import engine, get_db
from . import models, schemas, utils
from sqlalchemy.orm import Session

from .routers import post,user, auth, vote

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = "*",
    allow_credentials = True,
    allow_methods = "*",
    allow_headers = "*"
)

# pydantic model = defines the structure of a request and response. This emsures when a user wamts to create a post, the request will go through if it has a title, content in the body


# while True:
#     try:
#         conn = psycopg2.connect(host='localhost', database='fastapi', user = 'postgres', password='Harsh123', cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Database Connected")
#         break
#     except Exception as error:
#         print("Connecting to database failed")
#         print("Error : ", error)
#         time.sleep(2)

# my_posts = [{"title" : "Harsh", "content" : "Harsh Singh", "id" : 1}, {"title" : "Rishi", "content" : "Rishi Singh", "id" : 2}]

# def find_post(id):
#     for p in my_posts:
#         if(p["id"] == id):
#             return p

# def find_index_post(id):
#     for i, p in enumerate(my_posts):
#         if(p["id"] == id):
#             return i

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
async def root():
    return {"message" : "Hello Worldd"}

