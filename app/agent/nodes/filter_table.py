import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt


async def filter_table(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type":"progress", "step":"过滤表", "status":"running"})
    try:
        #1.获取状态中合并后表格列表，用户问题
        query = state["query"]
        table_infos = state["table_infos"]

        #2.调用大模型返回回答问题需要用到表格以及字段 大模型选择表格
        prompt = PromptTemplate(template=load_prompt("filter_table_info"), input_variables=["query", "table_infos"])
        chain = prompt | llm | JsonOutputParser()
        # {{
        #     "表名1": ["字段1", "字段2", "..."],
        #     "表名2": ["字段1", "字段2", "..."]
        # }}
        result = await chain.ainvoke({"query":query, "table_infos": yaml.dump(table_infos,allow_unicode=True, sort_keys=False)})
        #3.遍历表格列表，将不需要表格删除，将表中不需字段删除
        for table_info in table_infos[:]:
            table_name = table_info["name"]
            if table_name not in result:
                #将不需要表包含字段全部删除掉
                table_infos.remove(table_info)
            else:
                #回答问题需要的表，将表中不需要字段删除掉
                for column in table_info["columns"][:]:
                    column_name = column["name"]
                    if column_name not in result[table_name]:
                        table_info["columns"].remove(column)
        writer({"type":"progress", "step":"过滤表", "status":"success"})
        logger.info(f"过滤表成功：{[table_info['name'] for table_info in table_infos]}")
        logger.info(f"过滤字段成功：{[column['name'] for table_info in table_infos for column in table_info['columns']]}")
        #4.更新state中表格信息
        return {"table_infos": table_infos}
    except Exception as e:
        writer({"type":"progress", "step":"过滤表", "status":"error"})
        logger.error(f"过滤表失败, 错误信息: {str(e)}")
        raise
