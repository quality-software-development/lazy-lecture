from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from source.app.users.utils import create_admin
from source.core.database import database_health, get_db
from source.core.routers import api_router
from source.core.schemas import HealthSchema
from source.core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_admin()
    yield


app = FastAPI(title=settings.APP_TITLE, version=settings.VERSION, lifespan=lifespan)

app.include_router(api_router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_418_IM_A_TEAPOT,
        content=jsonable_encoder({"detail": str(exc)}),
    )


@app.get("/", response_model=HealthSchema, tags=["health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    return HealthSchema(api=True, database=await database_health(db=db))
