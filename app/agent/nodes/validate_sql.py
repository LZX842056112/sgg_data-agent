from langgraph.config import get_stream_writer
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 1.获取流写入器对象
    write = runtime.stream_writer
    write({"type": "progress", "step": "验证SQL", "status": "running"})

    # 2.具体逻辑
    try:
        write({"type": "progress", "step": "验证SQL", "status": "success"})

        return {"error": None}
    except Exception as e:
        logger.error(f"验证SQL发生异常：{e}")
        write({"type": "progress", "step": "验证SQL", "status": "error"})
        return {"error": f"{e}"}
