from datetime import datetime

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, DateInfoState, DBInfoState
from app.core.log import logger


async def add_extra_context(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "添加上下文", "status": "running"})
    try:
        # 1.获取当前时间 日期、星期、季度
        today = datetime.today()
        # 日期
        date = today.strftime("%Y-%m-%d")
        # 星期
        weekday = today.strftime("%A")
        # 季度
        quarter = f"Q{(today.month - 1) // 3 + 1}"
        date_info = DateInfoState(
            date=date,
            weekday=weekday,
            quarter=quarter
        )

        # 2.获取数据库信息 DW数据库管理系统名称，数据版本信息
        dw_mysql_repository = runtime.context["dw_mysql_repository"]
        db_info: dict[str, str] = await dw_mysql_repository.get_db_info()
        db_info_state = DBInfoState(
            dialect=db_info["dialect"],
            version=db_info["version"]
        )
        writer({"type": "progress", "step": "添加上下文", "status": "success"})
        logger.info(f"额外上下文信息：{db_info}, {date_info}")
        # 3.更新state中 日期信息 数据库信息
        return {"date_info": date_info, "db_info": db_info_state}
    except Exception as e:
        writer({"type": "progress", "step": "添加上下文", "status": "error"})
        logger.error(f"添加上下文失败, 错误信息: {str(e)}")
        raise
