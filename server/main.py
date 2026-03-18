from fastapi import FastAPI
from .api.v1.order import order_router
from .api.v1.stat import stat_router
from .api.v1.auth import auth_router

app = FastAPI()
app.include_router(order_router)
app.include_router(stat_router)
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"msg": "Service Platform API is running..."}
