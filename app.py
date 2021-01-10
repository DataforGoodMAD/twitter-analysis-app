#!/usr/bin/env python

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
import uvicorn

from src.api import api
from src.database import SQLALCHEMY_DATABASE_URL, Base, engine

app: FastAPI = FastAPI()

app.include_router(api.api)

origins=["http://localhost:8889"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/", include_in_schema=False)
async def api_root():
    return RedirectResponse(url="/docs/")


if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=8889, reload=True) 
