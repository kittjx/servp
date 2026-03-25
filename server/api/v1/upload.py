from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
import os
from datetime import datetime
import uuid

upload_router = APIRouter(prefix="/api/v1/upload")

# 上传目录配置
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


@upload_router.post("/image", status_code=status.HTTP_201_CREATED)
async def upload_image(file: UploadFile = File(...)):
    """
    上传单张图片
    """
    # 检查文件类型
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed. Only jpg, jpeg, png, gif, webp are allowed."
        )
    
    # 读取文件内容
    contents = await file.read()
    
    # 检查文件大小
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 10MB."
        )
    
    # 生成文件名
    ext = os.path.splitext(file.filename)[1]
    filename = f"{datetime.now().strftime('%Y%m%d')}/{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # 创建目录
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # 保存文件
    with open(filepath, "wb") as f:
        f.write(contents)
    
    # 返回文件URL
    return {
        "url": f"/uploads/{filename}",
        "filename": file.filename
    }


@upload_router.post("/images", status_code=status.HTTP_201_CREATED)
async def upload_images(files: List[UploadFile] = File(...)):
    """
    批量上传图片
    """
    if len(files) > 9:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 9 images allowed."
        )
    
    uploaded_urls = []
    
    for file in files:
        # 检查文件类型
        if not allowed_file(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} type not allowed. Only jpg, jpeg, png, gif, webp are allowed."
            )
        
        # 读取文件内容
        contents = await file.read()
        
        # 检查文件大小
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} too large. Maximum size is 10MB."
            )
        
        # 生成文件名
        ext = os.path.splitext(file.filename)[1]
        filename = f"{datetime.now().strftime('%Y%m%d')}/{uuid.uuid4()}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        # 创建目录
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 保存文件
        with open(filepath, "wb") as f:
            f.write(contents)
        
        uploaded_urls.append({
            "url": f"/uploads/{filename}",
            "filename": file.filename
        })
    
    return {
        "urls": uploaded_urls
    }


@upload_router.post("/avatar", status_code=status.HTTP_201_CREATED)
async def upload_avatar(file: UploadFile = File(...)):
    """
    Upload avatar (public endpoint for login)
    """
    # 检查文件类型
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed. Only jpg, jpeg, png, gif, webp are allowed."
        )
    
    # 读取文件内容
    contents = await file.read()
    
    # 检查文件大小
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 10MB."
        )
    
    # 生成文件名
    ext = os.path.splitext(file.filename)[1]
    filename = f"avatars/{datetime.now().strftime('%Y%m%d')}/{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # 创建目录
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # 保存文件
    with open(filepath, "wb") as f:
        f.write(contents)
    
    # 返回文件URL
    return {
        "url": f"/uploads/{filename}",
        "filename": file.filename
    }
