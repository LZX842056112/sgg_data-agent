from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def execute_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "执行SQL", "status": "running"})
    try:
        # 1.获取state中SQL语句
        sql = state["sql"]
        # 2.调用数仓持久层执行SQL查询
        dw_mysql_repository = runtime.context["dw_mysql_repository"]
        data = await dw_mysql_repository.execute_sql(sql)
        writer({"type": "progress", "step": "执行SQL", "status": "success"})
        logger.info(f"执行SQL结果：{data}")
        # 3.将查询结果实时返回
        writer({"type": "result", "data": data})
    except Exception as e:
        writer({"type": "progress", "step": "执行SQL", "status": "error"})
        logger.error(f"执行SQL异常：{str(e)}")
        raise
