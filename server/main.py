from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .api.v1.order import order_router
from .api.v1.stat import stat_router
from .api.v1.auth import auth_router
from .api.v1.upload import upload_router
import os

app = FastAPI()

# 配置静态文件目录（用于访问上传的图片）
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 注册路由
app.include_router(order_router)
app.include_router(stat_router)
app.include_router(auth_router)
app.include_router(upload_router)

@app.get("/")
def read_root():
    return {"msg": "Service Platform API is running..."}
