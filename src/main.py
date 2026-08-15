from src.api.v1.users import router as users_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(
    users_router,
    prefix="/api/v1/users",
    tags=["users"],
)
