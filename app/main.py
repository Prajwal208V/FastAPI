
from fastapi import FastAPI
from . import models #SQLALCHEMY
from .database import engine
from .routers import post,sqlalchemy_post,users

# Initialize the FastAPI application
app = FastAPI() 

models.Base.metadata.create_all(bind=engine)#SQLALCHEMY, it will create table within postgres

app.include_router(
    post.router,
    )
app.include_router(
    sqlalchemy_post.router,
)
app.include_router(
    users.router
)