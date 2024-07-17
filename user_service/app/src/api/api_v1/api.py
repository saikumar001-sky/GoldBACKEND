from fastapi import APIRouter
from src.api.api_v1.endpoints import user
from src.api.api_v1.endpoints import client
from src.api.api_v1.endpoints import payment

api_router = APIRouter()

api_router.include_router(user.router,prefix="/user", tags=["Authentication API's"])
api_router.include_router(client.router,prefix="/client", tags=["Client API's"])
api_router.include_router(payment.router,prefix="/payment", tags=["Payment API's"])