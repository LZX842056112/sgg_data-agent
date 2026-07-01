import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState, MetricInfoState
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt


async def filter_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type":"progress", "step":"过滤指标", "status":"running"})
    try:
        #1.获取合并后指标列表
        metric_infos= state["metric_infos"]
        query = state["query"]

        #2.调用大模型返回回答问题需要用到指标 大模型选择指标
        prompt = PromptTemplate(template=load_prompt("filter_metric_info"), input_variables=["query", "metric_infos"])
        chain = prompt | llm | JsonOutputParser()
        # [
        #     "指标名称1",
        #     "指标名称2"
        # ]
        result = await chain.ainvoke({"query":query, "metric_infos": yaml.dump(metric_infos,allow_unicode=True, sort_keys=False)})

        #3.遍历指标列表，将不需要指标删除 TODO 遍历中删除列表中元素 采用列表切片复制一个副本，底层：遍历使用副本，删除使用原列表
        for metric_info in metric_infos[:]:
            metric_name = metric_info["name"]
            if metric_name not in result:
                metric_infos.remove(metric_info)

        writer({"type":"progress", "step":"过滤指标", "status":"success"})
        logger.info(f"过滤指标成功：{[metric_info['name'] for metric_info in metric_infos]}")

        #4.封装state更新指标信息
        return {"metric_infos": metric_infos}
    except Exception as e:
        writer({"type":"progress", "step":"过滤指标", "status":"error"})
        logger.error(f"过滤指标失败, 错误信息: {str(e)}")
        raise

if __name__ == '__main__':
    users = [
        {"name": "张三", "age": 18},
        {"name": "李四", "age": 19},
        {"name": "王五", "age": 20}
    ]
    print(yaml.dump(users, allow_unicode=True, sort_keys=False))