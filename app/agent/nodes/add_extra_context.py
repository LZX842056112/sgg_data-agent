from langgraph.config import get_stream_writer
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def add_extra_context(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 1.获取流写入器对象
    write = runtime.stream_writer
    write({"type": "progress", "step": "添加上下文", "status": "running"})

    # 2.具体逻辑
    try:
        write({"type": "progress", "step": "添加上下文", "status": "success"})
    except Exception as e:
        logger.error(f"添加上下文发生异常：{e}")
        write({"type": "progress", "step": "添加上下文", "status": "error"})
        raise
