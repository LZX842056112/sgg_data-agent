import yaml
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt


async def correct_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "校正SQL", "status": "running"})
    try:
        # 1. 获取到生成SQL所需要的信息 表、指标、用户问题、时间、数据库信息、错误信息
        query = state["query"]
        table_infos = state["table_infos"]
        metric_infos = state["metric_infos"]
        db_info = state["db_info"]
        date_info = state["date_info"]
        error = state["error"]
        sql = state["sql"]

        # 2. 调用大模型对错误SQL进行修正
        prompt = PromptTemplate(template=load_prompt("correct_sql"),
                                input_variables=["table_infos", "metric_infos", "db_info", "date_info", "query",
                                                 "error",
                                                 "sql"])
        chain = prompt | llm | StrOutputParser()
        result = await chain.ainvoke({
            "query": query,
            "table_infos": yaml.dump(table_infos, allow_unicode=True, sort_keys=False),
            "metric_infos": yaml.dump(metric_infos, allow_unicode=True, sort_keys=False),
            "db_info": yaml.dump(db_info, allow_unicode=True, sort_keys=False),
            "date_info": yaml.dump(date_info, allow_unicode=True, sort_keys=False),
            "sql": sql,
            "error": error
        })
        writer({"type": "progress", "step": "校正SQL", "status": "success"})
        logger.info(f"校正SQL结果：{result}")
        # 3.更新状态中SQL
        return {"sql": result, "error": None}
    except Exception as e:
        writer({"type": "progress", "step": "校正SQL", "status": "error"})
        logger.error(f"校正SQL失败, 错误信息: {str(e)}")
        raise
