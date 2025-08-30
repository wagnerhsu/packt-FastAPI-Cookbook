# FastAPI 书店 API

这是一个使用 FastAPI 构建的简单书店 API 项目，包含书籍和作者管理功能。

## 项目结构

```
bookstore/
├── main.py          # 主应用文件
├── models.py        # Pydantic 数据模型
├── test_main.py     # 测试文件
├── requirements.txt # 项目依赖
└── README.md        # 项目说明文档
```

## 功能特性

- 📚 书籍信息查询 API
- 👨‍💼 作者信息查询 API
- ✅ 数据验证（使用 Pydantic）
- 🧪 单元测试覆盖
- 📖 自动生成 API 文档

## 安装依赖

1. 创建虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

2. 安装项目依赖：
```bash
pip install -r requirements.txt
```

3. 安装测试依赖：
```bash
pip install pytest httpx
```

## 运行应用

启动开发服务器：
```bash
uvicorn main:app --reload
```

应用将在 `http://localhost:8000` 启动。

## API 文档

启动服务器后，您可以访问以下地址查看自动生成的 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 获取书籍信息
- **GET** `/books/{book_id}`
- 参数：`book_id` (整数) - 书籍 ID
- 返回：书籍信息对象

示例响应：
```json
{
  "book_id": 9999,
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald"
}
```

### 获取作者信息
- **GET** `/authors/{author_id}`
- 参数：`author_id` (整数) - 作者 ID
- 返回：作者信息对象

## 数据模型

### Book 模型
- `title`: 字符串，长度 1-100 字符，必填
- `author`: 字符串，长度 1-50 字符，必填
- `year`: 整数，范围 1901-2099，必填

## 运行测试

### 使用 pytest 运行所有测试：
```bash
pytest
```

### 运行特定测试文件：
```bash
pytest test_main.py
```

### 运行测试并显示详细信息：
```bash
pytest -v
```

### 运行测试并显示覆盖率：
```bash
pytest --cov=main test_main.py
```

## 测试说明

当前项目包含以下测试：
- `test_read_book_by_id()`: 测试根据 ID 获取书籍信息的功能

测试使用 FastAPI 的 `TestClient` 来模拟 HTTP 请求，确保 API 端点正常工作。

## 开发说明

### 添加新的 API 端点
1. 在 `main.py` 中添加新的路由函数
2. 在 `models.py` 中定义相关的数据模型（如需要）
3. 在 `test_main.py` 中添加对应的测试用例

### 运行开发服务器
```bash
uvicorn main:app --reload --port 8000
```

`--reload` 选项会在代码更改时自动重启服务器。

## 依赖说明

- **FastAPI**: 现代、快速的 Python Web 框架
- **uvicorn**: ASGI 服务器，用于运行 FastAPI 应用
- **pydantic**: 数据验证和设置管理库
- **pytest**: Python 测试框架
- **httpx**: 现代 HTTP 客户端，用于测试

## 许可证

本项目是学习和演示用途的示例代码。

---

📚 这个项目是《FastAPI Cookbook》第一章的示例代码，展示了如何创建一个基本的 FastAPI 应用。
