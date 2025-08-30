import os
import shutil
from pathlib import Path
from typing import List

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse

app = FastAPI()

# 配置
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"}


def validate_file(file: UploadFile) -> None:
    """验证上传文件"""
    # 检查文件扩展名
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不允许的文件类型。允许的类型: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 检查文件大小（需要先读取一部分来估算）
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件太大。最大允许大小: {MAX_FILE_SIZE // (1024*1024)}MB"
        )


def sanitize_filename(filename: str) -> str:
    """清理文件名，防止路径遍历攻击"""
    # 移除路径分隔符和特殊字符
    safe_filename = Path(filename).name
    # 移除可能的危险字符
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    safe_filename = ''.join(c for c in safe_filename if c in safe_chars)
    return safe_filename or "unnamed_file"


@app.post("/uploadfile")
async def upload_file(file: UploadFile = File(...)):
    """
    上传文件到服务器

    - **file**: 要上传的文件

    返回上传成功的文件信息
    """
    try:
        # 验证文件
        validate_file(file)

        # 清理文件名
        safe_filename = sanitize_filename(file.filename)
        file_path = UPLOAD_DIR / safe_filename

        # 如果文件已存在，添加数字后缀
        counter = 1
        original_stem = file_path.stem
        while file_path.exists():
            file_path = UPLOAD_DIR / f"{original_stem}_{counter}{file_path.suffix}"
            counter += 1

        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "filename": file_path.name,
            "original_filename": file.filename,
            "size": file_path.stat().st_size,
            "message": "文件上传成功"
        }

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
    finally:
        await file.close()


@app.get("/downloadfile/{filename}", response_class=FileResponse)
async def download_file(filename: str):
    """
    下载指定文件

    - **filename**: 要下载的文件名

    返回文件内容
    """
    # 清理文件名，防止路径遍历
    safe_filename = sanitize_filename(filename)
    file_path = UPLOAD_DIR / safe_filename

    # 检查文件是否存在
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"文件 '{safe_filename}' 未找到"
        )

    # 确保文件在上传目录内（额外的安全检查）
    try:
        file_path.resolve().relative_to(UPLOAD_DIR.resolve())
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="访问被拒绝"
        )

    return FileResponse(
        path=str(file_path),
        filename=safe_filename,
        media_type='application/octet-stream'
    )


@app.get("/files/")
async def list_files():
    """
    列出所有可下载的文件

    返回文件列表
    """
    try:
        files = []
        for file_path in UPLOAD_DIR.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })
        return {"files": files, "count": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")


@app.delete("/deletefile/{filename}")
async def delete_file(filename: str):
    """
    删除指定文件

    - **filename**: 要删除的文件名

    返回删除结果
    """
    safe_filename = sanitize_filename(filename)
    file_path = UPLOAD_DIR / safe_filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"文件 '{safe_filename}' 未找到"
        )

    try:
        file_path.unlink()
        return {"message": f"文件 '{safe_filename}' 删除成功"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除文件失败: {str(e)}"
        )


@app.post("/uploadfiles")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """
    批量上传文件

    - **files**: 要上传的文件列表

    返回上传结果
    """
    results = []

    for file in files:
        try:
            validate_file(file)
            safe_filename = sanitize_filename(file.filename)
            file_path = UPLOAD_DIR / safe_filename

            # 处理重名文件
            counter = 1
            original_stem = file_path.stem
            while file_path.exists():
                file_path = UPLOAD_DIR / f"{original_stem}_{counter}{file_path.suffix}"
                counter += 1

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            results.append({
                "filename": file_path.name,
                "original_filename": file.filename,
                "status": "success",
                "size": file_path.stat().st_size
            })

        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
        finally:
            await file.close()

    return {"results": results, "total": len(files)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
