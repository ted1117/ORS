from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.database import dispose_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        yield
    finally:
        await dispose_database()


app = FastAPI(lifespan=lifespan)
