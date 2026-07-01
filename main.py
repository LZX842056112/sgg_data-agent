# 导入FastAPI核心类
import uuid
from urllib.request import Request

from fastapi import FastAPI

from app.api.routers.query_router import query_router
from app.core.context import request_id_ctx_var
from app.core.lifespan import lifespan

# 创建FastAPI应用实例
app = FastAPI(lifespan=lifespan)


# 绑定查询router
app.include_router(query_router)

# 添加中间件，在每个请求中生成唯一的request_id
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    # 调用路径函数之前
    request_id_ctx_var.set(uuid.uuid4())
    # 调用路径函数
    response = await call_next(request)
    # 调用路径函数之后
    return response



