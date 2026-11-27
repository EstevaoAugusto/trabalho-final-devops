from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import models  # noqa: F401  (registra os modelos no metadata)
from .database import Base, engine
from .routers import orders, products


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="E-commerce Service",
    description="Microsserviço básico de e-commerce: produtos e pedidos.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(products.router)
app.include_router(orders.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
