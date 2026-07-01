# 声明查询的路由
from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from app.api.dependencies import get_query_service
from app.api.schemas.query_schema import QuerySchema
from app.services.query_service import QueryService

query_router = APIRouter()


@query_router.post("/api/query")
async def query(query: QuerySchema, query_service:QueryService = Depends(get_query_service)):
    """
     前后端约定提交参数 采用请求体：{"query":"统计各分类销售商品数量"}
    :param query: 问题
    :return: 异步流式返回
        进度展示 约定{type:"progress",step:"找回字段","status":"running"}
        数据展示 约定{type:"result","data":业务数据}
        sse协议：data: 数据 \n\n
    """
    return StreamingResponse(query_service.query_answer(query.query), media_type="text/event-stream")