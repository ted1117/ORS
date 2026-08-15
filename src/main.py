from fastapi import FastAPI

from src.api.v1.ratings import router as ratings_router

app = FastAPI()

app.include_router(
    ratings_router,
    prefix="/api/v1/video-ratings",
    tags=["video-ratings"],
)
