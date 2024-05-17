from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.database import OrmMethods
from src.services import parse_data
from src.router import router_api, router_stream


@asynccontextmanager
async def lifespan(app: FastAPI):
    await OrmMethods.delete_tables()
    await OrmMethods.create_tables()
    print("The database is cleaned and ready to go")
    await parse_data()
    print("Date parsed successfully")
    yield
    print("Shutdown")


app = FastAPI(lifespan=lifespan)
app.include_router(router_api)
app.include_router(router_stream)
